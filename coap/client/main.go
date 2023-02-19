package main

import (
  "log"
  "flag"
  
  coap "github.com/go-ocf/go-coap"
)

func main() {
  c := &coap.Client{}

  log.Printf("Client handler: %v", c.Handler)
 
  co, err := c.Dial("localhost:5688")
  if err != nil {
    log.Fatalf("Error dialing: %v", err)
  }

  filename := flag.String("file", "100B", "file to fetch")
  flag.Parse()

  resp, err := co.Get(*filename)

  if err != nil {
    log.Fatalf("Error sending message: %v", err)
  }

  log.Printf("Response: %v", resp.AllOptions())
}
