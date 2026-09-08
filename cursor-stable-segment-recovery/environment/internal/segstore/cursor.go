package segstore

import "errors"

func BuildView(store, decisionsPath, provenancePath, viewPath string) error {
	return errors.New("recovery views are not implemented")
}

func ResolveCursor(store, cursorPath, viewPath string) error {
	return errors.New("cursor resolution is not implemented")
}
