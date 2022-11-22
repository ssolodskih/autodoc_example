# Container modules

## Main

```{mermaid}
sequenceDiagram
    autonumber
    Actor bvc as BioViewer Core
    participant m as Model
    participant tc as Type Checker
    participant c as Converter
    participant val as Validator
    participant cal as Calculator
    participant vis as Visualizer
    participant sm as Storage Manager
    participant s as Storage
    
    bvc -)+ m: Process [data] in <br>external_format
    activate bvc
    m ->>+ tc: Parse [data]
    tc ->> tc: Parses [data], validates its <br>structure and field types
    
    alt [data] is valid
        tc -->> m: Pydantic object <br>(data_definitions.InputPackage)
        m ->>+ c: Convert [data] to internal format <br>(data_definntions.InternalFormat)
        c ->> c: Converts [data] to internal <br>format, retains original [data]
        c -->>- m: [data] in internal format
        m ->>+ val: Validate [data]
    else [data] is invalid
        tc ->>- m: Raises ModelTypeCheckException
        m -->> bvc: Message with error description <br>(data_definitions.OutputPackage)
    end
    
    alt [data] is valid
        val -->> m: Data is valid
        m ->>+ cal: Calculate resistances
        cal ->> cal: Calculates resistances <br>using embedded sqlite DB
        cal -->>- m: Resistances
        m -->+ vis: Visualize resistances
        vis ->> vis: Visualizes resistances using SVG <br>template and renders it to PNG
        vis -->>- m: Resistances PNG image in base64 format
        m ->> m: Concatenate all intermediate data <br>(data_definitions.IntermediateData)
        m ->>+ sm: Store intermediate data
        sm ->>- s: Intermediate data
        m ->> m: Convert visualization results to client-specific <br>message (data_definitions.OutputPackage)
        m --) bvc: Client-specific message <br>(data_definitions.OutputPackage)
    else [data] is invalid (reference intervals invalidated)
        val -->>- m: Raises ModelValidationException
        m -->>- bvc: Message with error description <br>(data_definitions.OutputPackage)
    end
    deactivate bvc 
```

```{eval-rst}
.. automodule:: main
    :show-inheritance:
    :members: parse
```

## Model


```{eval-rst}
.. automodule:: model
    :show-inheritance:
    :members: parse
```

## Model Method


```{eval-rst}
.. automodule:: method
    :show-inheritance:
    :members: parse
```

## Abstracts


```{eval-rst}
.. automodule:: abstracts
    :show-inheritance:
    :members: parse
```

## Exceptions


```{eval-rst}
.. automodule:: exceptions
    :show-inheritance:
    :members: parse
```


## RabbitMQ helper


```{eval-rst}
.. automodule:: rabbit
    :show-inheritance:
    :members: parse
```
