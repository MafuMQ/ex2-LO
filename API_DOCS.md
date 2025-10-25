# API Documentation

## Base URL

    http://..

---

## POST /api/optimize

Optimize a set of variables with a budget constraint.

### Request
- **Content-Type:** application/json
- **Body:**

```
{
  "variables": [
    {
      "name": "string",
      "lowerBound": integer,
      "upperBound": integer | null,
      "profit": float,
      "integer": boolean,
      "multiplier": float
    },
    ...
  ],
  "budget": integer
}
```

#### Example
```
{
  "variables": [
    {
      "name": "coffee cake",
      "lowerBound": 0,
      "upperBound": null,
      "profit": 1.80,
      "integer": true,
      "multiplier": 8
    }
    // ... more variables ...
  ],
  "budget": 100
}
```

### Response
- **Content-Type:** application/json
- **Body:**

```
{
  "max_profit": float,
  "result": {
    "variable_name": value,
    ...
  }
}
```

#### Example
```
{
  "max_profit": 42.5,
  "result": {
    "coffee cake": 8,
    "chocolate cake": 12
  }
}
```

### Error Responses
- **400 Bad Request**: Invalid input
- **500 Internal Server Error**: Optimization or server error

---

## Notes
- All values must be provided in the correct type.
- The endpoint does not modify server state; it only returns the optimization result for the provided input.
