
#### Jinja Filter: require

Abort with an error message if the value is not a truthy value (i.e. a non-empty
string, non-zero integer etc), otherwise return the value.

This is useful for situations where it is better to abort if an expression is
expected to have a value, but doesn't, rather than make assumptions.

```jinja
Dear Bob,

Your flight details have changed and your flight will now depart at
{{ flight_time | require('flight_time must be a non-empty string') }}.

Don't be late.
```
