package segstore

// Recover follows the sealed coherent lineage, authenticates resynchronization
// after bounded damage, and keeps the complete transaction identity.
func Recover(store, statePath, decisionsPath, provenancePath string) error {
	m, err := readManifest(store)
	if err != nil {
		return err
	}
	slot, err := chooseAuthoritative(m)
	if err != nil {
		return err
	}
	frames, err := scanFrames(store, slot, false)
	if err != nil {
		return err
	}
	return emitRecovery(statePath, decisionsPath, provenancePath, assemble(frames, true))
}
