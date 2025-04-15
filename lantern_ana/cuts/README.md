# Cut definitions

We define cut functions that we apply per event.

They should take this form:

```
def mycut( input, params ):
    ...
    (Perform logic here)
    ...
    return result
```

where the arguments and return are

  * `input`: the ntuple tree
  * `params`: a dictionary with parameters passed along
  * `result`: True or False


