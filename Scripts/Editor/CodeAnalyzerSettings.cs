using UnityEngine;

namespace Expecto
{
    [CreateAssetMenu(fileName = "CodeAnalyzerSettings", menuName = "Expecto/CodeAnalyzerSettings")]
    public class CodeAnalyzerSettings : ScriptableObject
    {
        [Tooltip("CodeAnalyzer will analyze only classes from these namespaces")]
        public string[] namespaceFilters;

        [Tooltip("Output directory for generated XML files")]
        public string outputDirectory;
    }
}