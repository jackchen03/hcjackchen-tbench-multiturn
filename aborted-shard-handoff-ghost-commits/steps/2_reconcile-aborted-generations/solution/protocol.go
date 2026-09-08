package sim

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sort"
)
type Event struct { Kind, Shard, Owner, Source, Destination, Node, Incarnation, Op, Value, Action, Issuer, Boundary string; Generation, Sequence, Balance, Amount int; Nodes, Coverage []string }
type Shard struct { Owner string `json:"owner"`; Generation int `json:"generation"`; Values []string `json:"values"`; Balance int `json:"balance"` }
type Record struct { Key string `json:"key"`; Shard string `json:"shard"`; Node string `json:"node"`; Incarnation string `json:"incarnation"`; Op string `json:"op"`; Reply string `json:"reply"`; Generation int `json:"generation"`; Sequence int `json:"sequence"`; Applied bool `json:"applied"`; Replied bool `json:"replied"`; Value string `json:"value,omitempty"`; Amount int `json:"amount,omitempty"` }
type Output struct { Shards map[string]*Shard `json:"shards"`; Records []*Record `json:"records"`; Certificate []string `json:"certificate"` }
func ticketKey(e Event)string{return fmt.Sprintf("%s|%d|%s|%d",e.Shard,e.Generation,e.Incarnation,e.Sequence)}
func Run(path string,out io.Writer)error{
	f,err:=os.Open(path);if err!=nil{return err};defer f.Close();shards:=map[string]*Shard{};records:=map[string]*Record{};cert:=[]string{};reconciled:=map[string]bool{};finalized:=map[string]int{};scan:=bufio.NewScanner(f)
	for scan.Scan(){var e Event;if json.Unmarshal(scan.Bytes(),&e)!=nil||e.Kind==""{return fmt.Errorf("invalid")};key:=ticketKey(e);switch e.Kind{
	case"init":shards[e.Shard]=&Shard{Owner:e.Owner,Generation:e.Generation,Values:[]string{},Balance:e.Balance}
	case"begin":s:=shards[e.Shard];if s==nil{return fmt.Errorf("invalid")};if e.Generation>s.Generation{s.Owner=e.Destination;s.Generation=e.Generation;reconciled[e.Shard]=false}
	case"admit":if shards[e.Shard]==nil{return fmt.Errorf("invalid")};if _,ok:=records[key];!ok{records[key]=&Record{Key:key,Shard:e.Shard,Node:e.Node,Generation:e.Generation,Incarnation:e.Incarnation,Sequence:e.Sequence,Op:e.Op,Value:e.Value,Amount:e.Amount}}
	case"deliver":r:=records[key];s:=shards[e.Shard];if r==nil||s==nil{continue};if !r.Applied{if r.Op=="append"{old:=len(s.Values);s.Values=append(s.Values,r.Value);r.Reply=fmt.Sprintf("append:%d->%d",old,old+1)}else if r.Op=="debit"{old:=s.Balance;s.Balance-=r.Amount;r.Reply=fmt.Sprintf("debit:%d->%d",old,s.Balance)}else{return fmt.Errorf("invalid")};r.Applied=true};r.Node=e.Node
	case"ack":if r:=records[key];r!=nil&&r.Applied{r.Replied=true}
	case"retry":if r:=records[key];r==nil||!r.Applied{return fmt.Errorf("invalid")}
	case"crash","recover":
	case"abort":s:=shards[e.Shard];if s!=nil&&e.Generation==s.Generation{s.Owner=e.Source}
	case"control":s:=shards[e.Shard];if s!=nil&&e.Generation==s.Generation{if e.Action=="finalize"||e.Action=="abort"{s.Owner=e.Node}}
	case"reconcile":s:=shards[e.Shard];if s!=nil&&e.Destination==s.Owner{for _,r:=range records{if r.Shard==e.Shard{r.Node=e.Destination}};reconciled[e.Shard]=true}
	case"finalize":s:=shards[e.Shard];if s!=nil&&e.Generation==s.Generation&&e.Destination==s.Owner{finalized[e.Shard]=e.Generation}
	case"gc":s:=shards[e.Shard];if s!=nil&&e.Issuer==s.Owner&&finalized[e.Shard]==s.Generation&&reconciled[e.Shard]{for _,k:=range e.Coverage{if r:=records[k];r!=nil&&r.Shard==e.Shard{delete(records,k);cert=append(cert,k)}};sort.Strings(cert)}
	default:return fmt.Errorf("invalid")}}
	if scan.Err()!=nil{return scan.Err()};keys:=make([]string,0,len(records));for k:=range records{keys=append(keys,k)};sort.Strings(keys);rs:=make([]*Record,0,len(keys));for _,k:=range keys{rs=append(rs,records[k])};return json.NewEncoder(out).Encode(Output{Shards:shards,Records:rs,Certificate:cert})}
