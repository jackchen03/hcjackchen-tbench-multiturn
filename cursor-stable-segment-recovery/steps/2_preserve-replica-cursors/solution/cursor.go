package segstore

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

type ViewItem struct {
	Identity  Identity   `json:"identity"`
	Intervals []Interval `json:"intervals"`
	Order     int        `json:"order"`
}
type ViewFile struct {
	Branch         string            `json:"branch"`
	Bridges        []Bridge          `json:"bridges"`
	DecisionDigest string            `json:"decision_digest"`
	Generation     int               `json:"generation"`
	Items          []ViewItem        `json:"items"`
	SourceHashes   map[string]string `json:"source_hashes"`
	Version        int               `json:"version"`
}
type Cursor struct {
	Branch     string `json:"branch"`
	Generation int    `json:"generation"`
	Segment    int    `json:"segment"`
	Offset     int    `json:"offset"`
}
type CursorResult struct {
	Boundary int        `json:"boundary"`
	Replay   []Identity `json:"replay"`
}

func sourceHashes(store string, segments []int) (map[string]string, error) {
	out := map[string]string{}
	paths := []string{"manifest.json"}
	for _, s := range segments {
		paths = append(paths, filepath.Join("segments", fmt.Sprintf("seg-%04d.dat", s)))
	}
	for _, rel := range paths {
		h, e := fileHash(filepath.Join(store, rel))
		if e != nil {
			return nil, e
		}
		out[filepath.ToSlash(rel)] = h
	}
	return out, nil
}

func BuildView(store, decisionsPath, provenancePath, viewPath string) error {
	var ds DecisionsFile
	if err := readJSON(decisionsPath, &ds); err != nil {
		return err
	}
	var prov ProvenanceFile
	if err := readJSON(provenancePath, &prov); err != nil {
		return err
	}
	if ds.Version != 1 || prov.Version != 1 {
		return errors.New("unsupported recovery artifact version")
	}
	if len(ds.Transactions) != len(prov.Decisions) {
		return errors.New("decision/provenance mismatch")
	}
	m, err := readManifest(store)
	if err != nil {
		return err
	}
	slot, err := chooseAuthoritative(m)
	if err != nil {
		return err
	}
	hashes, err := sourceHashes(store, slot.Segments)
	if err != nil {
		return err
	}
	b, err := os.ReadFile(decisionsPath)
	if err != nil {
		return err
	}
	sum := sha256.Sum256(b)
	view := ViewFile{Branch: slot.Branch, Bridges: slot.Bridges, DecisionDigest: hex.EncodeToString(sum[:]), Generation: slot.Generation, SourceHashes: hashes, Version: 1}
	for _, d := range ds.Transactions {
		if d.Status == "accepted" {
			iv := append([]Interval(nil), d.Intervals...)
			sortIntervals(iv)
			view.Items = append(view.Items, ViewItem{d.Identity, iv, d.Order})
		}
	}
	sort.Slice(view.Items, func(i, j int) bool {
		if view.Items[i].Order != view.Items[j].Order {
			return view.Items[i].Order < view.Items[j].Order
		}
		return idKey(view.Items[i].Identity, true) < idKey(view.Items[j].Identity, true)
	})
	return writeCanonical(viewPath, view)
}

func atOrBefore(seg, end int, c Cursor) bool {
	return seg < c.Segment || (seg == c.Segment && end <= c.Offset)
}
func inside(iv Interval, c Cursor) bool {
	return iv.Segment == c.Segment && c.Offset >= iv.Start && c.Offset < iv.End
}

func ResolveCursor(store, cursorPath, viewPath string) error {
	var view ViewFile
	if err := readJSON(viewPath, &view); err != nil {
		return err
	}
	if view.Version != 1 {
		return errors.New("unsupported view version")
	}
	for rel, want := range view.SourceHashes {
		got, e := fileHash(filepath.Join(store, rel))
		if e != nil {
			return e
		}
		if got != want {
			return fmt.Errorf("source hash mismatch: %s", rel)
		}
	}
	var c Cursor
	if err := readJSON(cursorPath, &c); err != nil {
		return err
	}
	if c.Offset < 0 {
		return errors.New("negative cursor offset")
	}
	boundary := -1
	if c.Branch != view.Branch || c.Generation != view.Generation {
		for _, b := range view.Bridges {
			if b.FromBranch == c.Branch && b.FromGeneration == c.Generation && b.FromSegment == c.Segment && c.Offset >= b.FromStart && c.Offset < b.FromEnd {
				if boundary != -1 {
					return errors.New("ambiguous lineage bridge")
				}
				boundary = b.Boundary
			}
		}
		if boundary < 0 {
			return errors.New("cursor has no lineage bridge")
		}
	} else {
		boundary = 0
		for i, item := range view.Items {
			contained := false
			ackEndSeg, ackEnd := -1, -1
			for _, iv := range item.Intervals {
				if inside(iv, c) {
					contained = true
				}
				if iv.Envelope == "ack" && (iv.Segment > ackEndSeg || (iv.Segment == ackEndSeg && iv.End > ackEnd)) {
					ackEndSeg, ackEnd = iv.Segment, iv.End
				}
			}
			if contained {
				boundary = i
				break
			}
			if ackEndSeg >= 0 && atOrBefore(ackEndSeg, ackEnd, c) {
				boundary = i + 1
			}
		}
	}
	if boundary < 0 || boundary > len(view.Items) {
		return errors.New("cursor boundary out of range")
	}
	replay := make([]Identity, 0, len(view.Items)-boundary)
	for _, item := range view.Items[boundary:] {
		replay = append(replay, item.Identity)
	}
	return writeCanonical("/dev/stdout", CursorResult{Boundary: boundary, Replay: replay})
}
