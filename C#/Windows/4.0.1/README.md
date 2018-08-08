# Velocity Scripting for C# (4.0.1.819)

## Installation

The Velocity C# scripting API is bundled as a single C# 
assembly.  Simply reference the `Velocity.CSharp.dll` 
assembly in your project.

In Visual Studio:

- Right-click `References` in your C# project.
- Select `Add Reference`.
- Select `Browse` from the left-most column.
- Click the `Browse` button and select the `Velocity.CSharp.dll` file.

## Usage

Example scripts are provided in the `examples` folder next to 
the assembly.  The main entry point is the `VelocityEngine` class.

As a best practice, you should use `AppDomain.CurrentDomain.ProcessExit` 
to ensure the engine is logged out when the script exits.  This is to ensure 
the license consumed by the login session is freed.

```csharp
var engine = new VelocityEngine();
AppDomain.CurrentDomain.ProcessExit += (source, data) => { engine.logout(); };
// login and use the engine here
```

Doc comments are included in `Velocity.CSharp.xml` and will be available 
in your IDE's interface as long as this file remains next to the assembly DLL.
For example, in Visual Studio, hovering on a class or method will show the 
doc comments in a floating window.

