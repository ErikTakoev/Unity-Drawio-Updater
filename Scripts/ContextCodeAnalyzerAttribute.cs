using System;

namespace Expecto
{
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method | AttributeTargets.Field)]
    public class ContextCodeAnalyzerAttribute : Attribute
    {
        public string Context { get; }
        public ContextCodeAnalyzerAttribute(string context)
        {
#if UNITY_EDITOR
            Context = context;
#endif
        }
    }
}