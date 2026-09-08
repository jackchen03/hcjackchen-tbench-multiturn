package segstore

import (
	"errors"
	"sort"
)

// Recover is the legacy implementation. It is intentionally close enough to
// be useful for diagnosis, but its authority and resynchronization assumptions
// are known to be unsafe on the incident stores.
func Recover(store, statePath, decisionsPath, provenancePath string) error {
	m, err := readManifest(store)
	if err != nil {
		return err
	}
	var candidates []Slot
	for _, s := range m.Slots {
		if s.Checksum == slotChecksum(s) {
			candidates = append(candidates, s)
		}
	}
	if len(candidates) == 0 {
		return errors.New("no valid manifest slot")
	}
	sort.Slice(candidates, func(i, j int) bool { return candidates[i].Sequence > candidates[j].Sequence })
	frames, err := scanFrames(store, candidates[0], true)
	if err != nil {
		return err
	}
	return emitRecovery(statePath, decisionsPath, provenancePath, assemble(frames, false))
}
