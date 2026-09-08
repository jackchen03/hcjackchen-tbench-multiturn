package main

import (
	"os"

	"example.com/segstore/internal/segstore"
)

func main() {
	os.Exit(segstore.Main(os.Args[1:]))
}
