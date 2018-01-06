# window-specification-generator

Generate a pdf of window (physical windows, the ones that goes into you house) specification from a JSON description.
In other words given this:
```
{
    "name": "example",
    "title": "Example",
    "windows": [
        {
            "name": "kitchen1",
            "width": 100,
            "height": 100,
            "division": {
                "type": "vertical",
                "pieces": [
                    {
                        "type": "horizontal",
                        "pieces": [
                            {}, {"opens": "left"}
                        ]
                    },
                    {
                        "opens": ["top", "left"]
                    }
                ]
            }
        }
 }
 ```

Generate this:
![screenshot-example](./screenshot-example.png)

## Usage

```
./wsg.py /path/to/my-json-specification.json
```

## Dependencies

* [python3](https://www.python.org/)
* [reportlab](http://www.reportlab.com/) (available from pip)
