package main

import (
  "flag"
  "io"
  "log"
  "os"
  "path"

  coap "github.com/go-ocf/go-coap"
)

func handleFile(root string) coap.HandlerFunc {
  handler := func(w coap.ResponseWriter, req *coap.Request) {
    w.SetContentFormat(coap.AppOctets)

    fname := path.Join(root, req.Msg.PathString())
    f, err := os.Open(fname);
    if err != nil {
      log.Printf("Cannot open file %v: %v", fname, err)
    }

    if _, err := io.Copy(w, f); err != nil {
      log.Printf("Failed to write response: %v", err)
    }
  }

  return handler
}

func main() {
  listenerErrorHandler := func(err error) bool {
		log.Printf("Listener error occurred: %v", err)
		return true
	}

  root := flag.String("root", ".", "directory to serve files from")
  flag.Parse()

  log.Printf("Root directory: %v", *root)

  log.Fatal(coap.ListenAndServe("udp", ":5688", coap.HandlerFunc(handleFile(*root)), listenerErrorHandler))
}
