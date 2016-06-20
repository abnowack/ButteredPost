# This is a test

- a big
- test

$\alpha = 2 *i* j $

<pyx>
a = 2+2
print a + 6
</pyx>

- [ ] Task 1
- [ ] Task 2
- [x] Task 33   
- [ ] Oh no

Test

- [ ] foo
- [x] bar
- [ ] baz

```python
@contextlib.contextmanager
def stdout_io(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old
```