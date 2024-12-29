# SVLang, a toy language for the SVC16 "Simplest Virtual Computer"

**NOTE:** This is a WIP. At the moment, the compiler isn't implemented, only
the parser and type checker.

This repository contains the implementation for SVLang, a simple language for
the [SVC16 "Simplest Virtual Computer"](https://github.com/JanNeuendorf/SVC16).

## The SVLang Language

SVLang is a simple language with loops and branches. It is strongly typed.

The syntax is inspired by Python's, PHP's and C's.

Variables are prefixed with a `$` dollar sign, while functions are not.

The following types are available: `BOOL`, `UINT`, `COLOR`.

Here is a simple program that shows a white pixel where the cursor is:

```
while True {
  setPixel($MOUSE_X, $MOUSE_Y, #FFFF)
  sync()
}
```

Here is a slightly more complex program that shows a gradient, and flashes the
background blue if the left mouse button is pressed:

```
while True {
    $x: UINT = 0
    while $x < 256 {
        $x = $x + 1
        $y: UINT = 0
        while $y < 256 {
            $y = $y + 1
            $blue: UINT = 0
            if $MOUSE_LMB {
                $blue = 255
            }
            setPixel($x, $y, Color($x, $y, $blue))
        }
    }
    sync()
}
```

SVLang defines the following builtin variables and functions:
- `$MOUSE_X`, `$MOUSE_Y`: The cursor position as UINTs, going from 0 to 255 inclusive.
- `$MOUSE_LMB`, `$MOUSE_RMB`: Which mouse buttons are pressed, as BOOLs.
- `$BUTTON_A`, `$BUTTON_B`, `$BUTTON_UP`, `$BUTTON_DOWN`, `$BUTTON_LEFT`, `$BUTTON_RIGHT`, `$BUTTON_SELECT`, `$BUTTON_START`: Which buttons are pressed, as BOOLs.
- `Color($red: UINT, $green: UINT, $blue: UINT)`: Build a COLOR from 8-bit red, green and blue components.
- `sync()`: Flush the display buffer, and update the mouse coordinates and buttons status.
- `setPixel($x: UINT, $y: UINT, $color: COLOR)`: Set the color of a pixel

## Tools provided

### Compiler

Compile SVLang programs into SVC16 binaries

Usage
```bash
# Compile SVLang program to SVC16 binary
python compile.py input.svl output.svc16
```
