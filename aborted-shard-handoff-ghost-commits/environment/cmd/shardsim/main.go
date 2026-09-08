package main

import (
  "flag"
  "fmt"
  "os"
  "shardsim/internal/sim"
)

func main() {
  if len(os.Args) < 2 || os.Args[1] != "run" { fmt.Fprintln(os.Stderr, "usage: shardsim run --scenario NAME --trace PATH"); os.Exit(2) }
  fs := flag.NewFlagSet("run", flag.ContinueOnError)
  scenario := fs.String("scenario", "public", "scenario label")
  trace := fs.String("trace", "", "JSONL trace")
  if fs.Parse(os.Args[2:]) != nil || *trace == "" { os.Exit(2) }
  _ = scenario
  if err := sim.Run(*trace, os.Stdout); err != nil { fmt.Println(`{"error":"invalid_event"}`); os.Exit(1) }
}
