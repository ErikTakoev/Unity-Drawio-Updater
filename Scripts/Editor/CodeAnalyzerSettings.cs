using UnityEngine;

namespace Expecto
{
    [CreateAssetMenu(fileName = "CodeAnalyzerSettings", menuName = "Expecto/CodeAnalyzerSettings")]
    public class CodeAnalyzerSettings : ScriptableObject
    {
        public string[] namespaceFilters;
        public string outputDirectory;
    }
}