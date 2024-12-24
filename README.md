# SVLang, a toy language for the SVC16 "Simplest Virtual Computer"

This repository contains the implementation for SVLang, a simple language for
the [SVC16 "Simplest Virtual Computer"](https://github.com/JanNeuendorf/SVC16).

It also contains a compiler for SVAssembly, a superset of the assembly shown in
[SVC16's README.md](https://github.com/JanNeuendorf/SVC16/blob/main/README.md#example).

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
            if $MOUSE_LEFT {
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

### Compiler/Assembler

Compile SVLang programs into SVC16 binaries or SVAssembly.

Usage
```bash
# Compile SVLang program to SVC16 binary
python compile.py input.svl output.svc16
# Compile SVLang program to SVAssembly
python compile.py input.svl --output-format sva output.sva
# Assemble SVAssembly to SVC16 binary
python compile --input-format sva input.sva output.svc16
```

### Decompiler

Decompiles SVC16 binaries into SVAssembly.

**Note:** The decompiler will stop decompiling at the first invalid instruction
encountered.

Usage:
```bash
# Print assembly to stdout
python decompiler.py program.svc16
# Write assembly to a file
python decompiler.py program.svc16 program.sva
```
