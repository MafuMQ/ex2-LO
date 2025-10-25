# API Documentation

## Base URL

  https://ex2-lo.vercel.app

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
      "integer": boolean,
      "multiplier": float,
      // One of the following must be provided:
      // - profit (float)
      // - unit_selling_price (float)
      // - profit_per_dollar (float)
      // If profit is omitted, it will be calculated from unit_selling_price or profit_per_dollar.
      "profit": float,                // optional if unit_selling_price or profit_per_dollar is given
      "unit_selling_price": float,    // optional
      "profit_per_dollar": float      // optional
    },
    ...
  ],
  "budget": integer
}
```

#### Example 1: Direct profit
```
{
  "variables": [
    {
      "name": "classic cake",
      "lowerBound": 0,
      "upperBound": 10,
      "integer": true,
      "multiplier": 3,
      "profit": 2.0
    }
  ],
  "budget": 100
}
```

#### Example 2: Using unit_selling_price
```
{
  "variables": [
    {
      "name": "test cake",
      "lowerBound": 0,
      "upperBound": 10,
      "integer": true,
      "multiplier": 5,
      "unit_selling_price": 8
    }
  ],
  "budget": 100
}
```

#### Example 3: Using profit_per_dollar
```
{
  "variables": [
    {
      "name": "bonus cake",
      "lowerBound": 0,
      "upperBound": 10,
      "integer": true,
      "multiplier": 4,
      "profit_per_dollar": 0.5
    }
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
