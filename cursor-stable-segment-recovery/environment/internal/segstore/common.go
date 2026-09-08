package segstore

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"hash/crc32"
	"os"
	"path/filepath"
	"sort"
	"strconv"
)

type Parent struct {
	Branch     string `json:"branch"`
	Generation int    `json:"generation"`
	Sequence   int    `json:"sequence"`
}
type Anchor struct {
	Segment int    `json:"segment"`
	Offset  int    `json:"offset"`
	Digest  string `json:"digest"`
}
type Bridge struct {
	FromBranch     string `json:"from_branch"`
	FromGeneration int    `json:"from_generation"`
	FromSegment    int    `json:"from_segment"`
	FromStart      int    `json:"from_start"`
	FromEnd        int    `json:"from_end"`
	Boundary       int    `json:"boundary"`
}
type Slot struct {
	Branch      string   `json:"branch"`
	Generation  int      `json:"generation"`
	Sequence    int      `json:"sequence"`
	Sealed      bool     `json:"sealed"`
	Parent      *Parent  `json:"parent"`
	Segments    []int    `json:"segments"`
	DamageBound int      `json:"damage_bound"`
	Anchors     []Anchor `json:"anchors"`
	Bridges     []Bridge `json:"bridges"`
	Checksum    string   `json:"checksum"`
}
type Manifest struct {
	Slots []Slot `json:"slots"`
}
type Header struct {
	Kind        string `json:"kind"`
	Branch      string `json:"branch"`
	Generation  int    `json:"generation"`
	Segment     int    `json:"segment"`
	TxID        string `json:"txid"`
	Incarnation int    `json:"incarnation"`
	Envelope    string `json:"envelope"`
	Part        int    `json:"part"`
	Parts       int    `json:"parts"`
	Order       int    `json:"order"`
	Prev        string `json:"prev"`
}
type Identity struct {
	Branch      string `json:"branch"`
	Generation  int    `json:"generation"`
	TxID        string `json:"txid"`
	Incarnation int    `json:"incarnation"`
}
type Interval struct {
	Segment  int    `json:"segment"`
	Start    int    `json:"start"`
	End      int    `json:"end"`
	Envelope string `json:"envelope"`
}
type Frame struct {
	Header   Header
	Payload  []byte
	Interval Interval
	Digest   string
}
type Operation struct {
	Key   string `json:"key"`
	Op    string `json:"op"`
	Value string `json:"value,omitempty"`
}
type Decision struct {
	Identity        Identity    `json:"identity"`
	Intervals       []Interval  `json:"intervals"`
	OperationDigest string      `json:"operation_digest"`
	Order           int         `json:"order"`
	Reason          string      `json:"reason"`
	Status          string      `json:"status"`
	Operations      []Operation `json:"-"`
}
type DecisionsFile struct {
	Transactions []Decision `json:"transactions"`
	Version      int        `json:"version"`
}
type Applied struct {
	Identity Identity `json:"identity"`
	Key      string   `json:"key"`
	Op       string   `json:"op"`
	OpIndex  int      `json:"op_index"`
	Value    string   `json:"value,omitempty"`
}
type StateFile struct {
	Applied []Applied         `json:"applied"`
	Values  map[string]string `json:"values"`
	Version int               `json:"version"`
}
type ProvOp struct {
	Identity  Identity   `json:"identity"`
	Intervals []Interval `json:"intervals"`
	OpIndex   int        `json:"op_index"`
}
type ProvDecision struct {
	Identity  Identity   `json:"identity"`
	Intervals []Interval `json:"intervals"`
}
type ProvenanceFile struct {
	Decisions  []ProvDecision `json:"decisions"`
	Operations []ProvOp       `json:"operations"`
	Version    int            `json:"version"`
}

func fail(err error) int { fmt.Fprintln(os.Stderr, err); return 1 }

func Main(args []string) int {
	if len(args) == 0 {
		return fail(errors.New("usage: segstore recover|build-view|resolve-cursor ..."))
	}
	switch args[0] {
	case "recover":
		if len(args) != 8 || args[2] != "--state" || args[4] != "--decisions" || args[6] != "--provenance" {
			return fail(errors.New("usage: segstore recover STORE --state STATE --decisions DECISIONS --provenance PROVENANCE"))
		}
		return failIf(Recover(args[1], args[3], args[5], args[7]))
	case "build-view":
		if len(args) != 8 || args[2] != "--decisions" || args[4] != "--provenance" || args[6] != "--view" {
			return fail(errors.New("usage: segstore build-view STORE --decisions DECISIONS --provenance PROVENANCE --view VIEW"))
		}
		return failIf(BuildView(args[1], args[3], args[5], args[7]))
	case "resolve-cursor":
		if len(args) != 5 || args[3] != "--view" {
			return fail(errors.New("usage: segstore resolve-cursor STORE CURSOR --view VIEW"))
		}
		return failIf(ResolveCursor(args[1], args[2], args[4]))
	default:
		return fail(fmt.Errorf("unknown command %q", args[0]))
	}
}

func failIf(err error) int {
	if err != nil {
		return fail(err)
	}
	return 0
}

func readManifest(store string) (Manifest, error) {
	var m Manifest
	b, err := os.ReadFile(filepath.Join(store, "manifest.json"))
	if err != nil {
		return m, err
	}
	err = json.Unmarshal(b, &m)
	return m, err
}

func slotChecksum(s Slot) string {
	b, _ := json.Marshal(s)
	var obj map[string]any
	_ = json.Unmarshal(b, &obj)
	delete(obj, "checksum")
	b, _ = json.Marshal(obj)
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}

func slotID(s Slot) string {
	return s.Branch + ":" + strconv.Itoa(s.Generation) + ":" + strconv.Itoa(s.Sequence)
}

func chooseAuthoritative(m Manifest) (Slot, error) {
	byID := map[string]Slot{}
	valid := map[string]bool{}
	for _, s := range m.Slots {
		byID[slotID(s)] = s
		valid[slotID(s)] = s.Sealed && s.Checksum == slotChecksum(s)
	}
	var coherent func(Slot, map[string]bool) bool
	coherent = func(s Slot, seen map[string]bool) bool {
		id := slotID(s)
		if !valid[id] || seen[id] {
			return false
		}
		if s.Parent == nil {
			return true
		}
		seen[id] = true
		p, ok := byID[s.Parent.Branch+":"+strconv.Itoa(s.Parent.Generation)+":"+strconv.Itoa(s.Parent.Sequence)]
		return ok && coherent(p, seen)
	}
	var choices []Slot
	for _, s := range m.Slots {
		if coherent(s, map[string]bool{}) {
			choices = append(choices, s)
		}
	}
	if len(choices) == 0 {
		return Slot{}, errors.New("no coherent sealed manifest slot")
	}
	sort.Slice(choices, func(i, j int) bool {
		a, b := choices[i], choices[j]
		if a.Generation != b.Generation {
			return a.Generation > b.Generation
		}
		if a.Sequence != b.Sequence {
			return a.Sequence > b.Sequence
		}
		return a.Branch > b.Branch
	})
	return choices[0], nil
}

func parseFrame(data []byte, off, segment int) (Frame, int, error) {
	var f Frame
	if off+16 > len(data) || string(data[off:off+4]) != "SGF1" {
		return f, off, errors.New("bad magic")
	}
	hl := int(binary.BigEndian.Uint32(data[off+4 : off+8]))
	pl := int(binary.BigEndian.Uint32(data[off+8 : off+12]))
	hc := binary.BigEndian.Uint32(data[off+12 : off+16])
	end := off + 16 + hl + pl + 4 + 32
	if hl < 2 || pl < 0 || end > len(data) {
		return f, off, errors.New("bad length")
	}
	hb := data[off+16 : off+16+hl]
	if crc32.ChecksumIEEE(hb) != hc {
		return f, off, errors.New("bad header checksum")
	}
	pb := data[off+16+hl : off+16+hl+pl]
	pc := binary.BigEndian.Uint32(data[off+16+hl+pl : off+20+hl+pl])
	if crc32.ChecksumIEEE(pb) != pc {
		return f, off, errors.New("bad payload checksum")
	}
	want := data[end-32 : end]
	got := sha256.Sum256(data[off : end-32])
	if !bytes.Equal(want, got[:]) {
		return f, off, errors.New("bad frame digest")
	}
	if err := json.Unmarshal(hb, &f.Header); err != nil {
		return f, off, err
	}
	if f.Header.Segment != segment || f.Header.Parts < 1 || f.Header.Part < 0 || f.Header.Part >= f.Header.Parts {
		return f, off, errors.New("bad header fields")
	}
	if f.Header.Kind == "solo" && (f.Header.Parts != 1 || f.Header.Part != 0) {
		return f, off, errors.New("bad solo")
	}
	if f.Header.Parts > 1 && ((f.Header.Part == 0 && f.Header.Kind != "start") || (f.Header.Part == f.Header.Parts-1 && f.Header.Kind != "seal") || (f.Header.Part > 0 && f.Header.Part < f.Header.Parts-1 && f.Header.Kind != "continuation")) {
		return f, off, errors.New("bad multipart kind")
	}
	f.Payload = append([]byte(nil), pb...)
	f.Interval = Interval{Segment: segment, Start: off, End: end, Envelope: f.Header.Envelope}
	f.Digest = hex.EncodeToString(got[:])
	return f, end, nil
}

func anchorSet(s Slot) map[string]string {
	out := map[string]string{}
	for _, a := range s.Anchors {
		out[fmt.Sprintf("%d:%d", a.Segment, a.Offset)] = a.Digest
	}
	return out
}

func scanFrames(store string, s Slot, stopAtDamage bool) ([]Frame, error) {
	anchors := anchorSet(s)
	prev := string(bytes.Repeat([]byte{'0'}, 64))
	var out []Frame
	for _, seg := range s.Segments {
		b, err := os.ReadFile(filepath.Join(store, "segments", fmt.Sprintf("seg-%04d.dat", seg)))
		if err != nil {
			return nil, err
		}
		off := 0
		skipped := 0
		for off < len(b) {
			f, next, e := parseFrame(b, off, seg)
			valid := e == nil && f.Header.Branch == s.Branch && f.Header.Generation == s.Generation
			if valid {
				_, anchored := anchors[fmt.Sprintf("%d:%d", seg, off)]
				valid = (f.Header.Prev == prev) || (anchored && anchors[fmt.Sprintf("%d:%d", seg, off)] == f.Digest)
			}
			if valid {
				out = append(out, f)
				prev = f.Digest
				off = next
				skipped = 0
				continue
			}
			if stopAtDamage {
				break
			}
			off++
			skipped++
			if skipped > s.DamageBound {
				return nil, fmt.Errorf("damage exceeds bound in segment %d", seg)
			}
		}
	}
	return out, nil
}

type envelope struct {
	parts map[int]Frame
	count int
	order int
}
type tx struct {
	id  Identity
	env map[string]*envelope
}

func idKey(i Identity, full bool) string {
	if !full {
		return i.TxID
	}
	return fmt.Sprintf("%s\x00%d\x00%s\x00%d", i.Branch, i.Generation, i.TxID, i.Incarnation)
}

func assemble(frames []Frame, fullIdentity bool) []Decision {
	txs := map[string]*tx{}
	for _, f := range frames {
		id := Identity{f.Header.Branch, f.Header.Generation, f.Header.TxID, f.Header.Incarnation}
		k := idKey(id, fullIdentity)
		t := txs[k]
		if t == nil {
			t = &tx{id: id, env: map[string]*envelope{}}
			txs[k] = t
		}
		e := t.env[f.Header.Envelope]
		if e == nil {
			e = &envelope{parts: map[int]Frame{}, count: f.Header.Parts, order: f.Header.Order}
			t.env[f.Header.Envelope] = e
		}
		if e.count == f.Header.Parts && e.order == f.Header.Order {
			e.parts[f.Header.Part] = f
		}
	}
	complete := func(e *envelope) bool {
		if e == nil || len(e.parts) != e.count {
			return false
		}
		for i := 0; i < e.count; i++ {
			if _, ok := e.parts[i]; !ok {
				return false
			}
		}
		return true
	}
	var ds []Decision
	for _, t := range txs {
		var iv []Interval
		maxOrder := 0
		for _, e := range t.env {
			if e.order > maxOrder {
				maxOrder = e.order
			}
			for _, f := range e.parts {
				iv = append(iv, f.Interval)
			}
		}
		sortIntervals(iv)
		d := Decision{Identity: t.id, Intervals: iv, Order: maxOrder, Status: "rejected", Reason: "missing_data"}
		data, commit, ack, abort := t.env["data"], t.env["commit"], t.env["ack"], t.env["abort"]
		if complete(data) {
			var payload []byte
			for i := 0; i < data.count; i++ {
				payload = append(payload, data.parts[i].Payload...)
			}
			var body struct {
				Ops []Operation `json:"ops"`
			}
			if json.Unmarshal(payload, &body) == nil {
				d.Operations = body.Ops
				cb, _ := json.Marshal(body.Ops)
				h := sha256.Sum256(cb)
				d.OperationDigest = hex.EncodeToString(h[:])
			}
		}
		switch {
		case !complete(data):
			d.Reason = "missing_data"
		case !complete(commit):
			d.Reason = "missing_commit"
		case !complete(ack):
			d.Reason = "missing_ack"
		case complete(abort) && abort.order <= ack.order:
			d.Reason = "aborted"
		default:
			d.Status = "accepted"
			d.Reason = "accepted"
			d.Order = ack.order
		}
		ds = append(ds, d)
	}
	sort.Slice(ds, func(i, j int) bool {
		if ds[i].Order != ds[j].Order {
			return ds[i].Order < ds[j].Order
		}
		return idKey(ds[i].Identity, true) < idKey(ds[j].Identity, true)
	})
	return ds
}

func sortIntervals(v []Interval) {
	sort.Slice(v, func(i, j int) bool {
		if v[i].Segment != v[j].Segment {
			return v[i].Segment < v[j].Segment
		}
		if v[i].Start != v[j].Start {
			return v[i].Start < v[j].Start
		}
		if v[i].End != v[j].End {
			return v[i].End < v[j].End
		}
		return v[i].Envelope < v[j].Envelope
	})
}
func writeCanonical(path string, v any) error {
	b, err := json.Marshal(v)
	if err != nil {
		return err
	}
	var normalized any
	if err = json.Unmarshal(b, &normalized); err != nil {
		return err
	}
	b, err = json.Marshal(normalized)
	if err != nil {
		return err
	}
	b = append(b, '\n')
	if path == "/dev/stdout" {
		_, err = os.Stdout.Write(b)
		return err
	}
	tmp := path + ".tmp"
	if err = os.WriteFile(tmp, b, 0644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

func emitRecovery(statePath, decPath, provPath string, ds []Decision) error {
	state := StateFile{Version: 1, Values: map[string]string{}}
	prov := ProvenanceFile{Version: 1}
	for _, d := range ds {
		prov.Decisions = append(prov.Decisions, ProvDecision{d.Identity, d.Intervals})
		if d.Status != "accepted" {
			continue
		}
		for i, op := range d.Operations {
			a := Applied{Identity: d.Identity, Key: op.Key, Op: op.Op, OpIndex: i, Value: op.Value}
			state.Applied = append(state.Applied, a)
			if op.Op == "put" {
				state.Values[op.Key] = op.Value
			} else if op.Op == "delete" {
				delete(state.Values, op.Key)
			}
			prov.Operations = append(prov.Operations, ProvOp{d.Identity, d.Intervals, i})
		}
	}
	plain := make([]Decision, len(ds))
	copy(plain, ds)
	if err := writeCanonical(statePath, state); err != nil {
		return err
	}
	if err := writeCanonical(decPath, DecisionsFile{Transactions: plain, Version: 1}); err != nil {
		return err
	}
	return writeCanonical(provPath, prov)
}

func readJSON(path string, v any) error {
	b, e := os.ReadFile(path)
	if e != nil {
		return e
	}
	return json.Unmarshal(b, v)
}
func fileHash(path string) (string, error) {
	b, e := os.ReadFile(path)
	if e != nil {
		return "", e
	}
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:]), nil
}
