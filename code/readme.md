Once, before anything, initialize the python venv
```
source venv/bin/activate
```

# Running main.py
Make sure python is using the proper ket version (with the newly compilated kbw)
```
pip install -e ket
```

run the script

```
python main.py
```
# Making changes to kbw
After kbw source code is changed, recompile it
```
cargo build --release --manifest-path ket/src/ket/clib/libs/kbw/Cargo.toml
```