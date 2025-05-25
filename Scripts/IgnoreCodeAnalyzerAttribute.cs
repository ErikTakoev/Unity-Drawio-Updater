using System;

namespace Expecto
{
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method | AttributeTargets.Field)]
    public class IgnoreCodeAnalyzerAttribute : Attribute
    {
    }
}