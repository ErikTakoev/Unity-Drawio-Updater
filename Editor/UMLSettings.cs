using System.IO;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace Expecto
{
    [CreateAssetMenu(fileName = "UMLSettings", menuName = "Expecto/UML Settings")]
    public class UMLSettings : ScriptableObject
    {
        [Header("Python Settings")]
        [Tooltip("Path to the Python executable or python if it's available in PATH")]
        public string pythonPath = "python";

        [Tooltip("Path to the generate_uml.py script")]
        public string generateUMLPath = null;

        [Tooltip("Output directory for generated UML files")]
        public string outputDirectory = null;

        [Header("UML Settings")]

        [Tooltip("Automatically clean up classes that no longer exist in the codebase")]
        public bool cleanupClasses = false;

        [Tooltip("Automatically clean up associations for classes")]
        public bool cleanupAssociations = false;

        string GetCrossPlatformPath(string path)
        {
            // Нормалізуємо шлях для поточної ОС
            string normalizedPath = Path.GetFullPath(path);

            // Для шляхів, які будуть використовуватися в Python або веб-контексті,
            // можна замінити всі зворотні слеші на прямі
            string crossPlatformPath = normalizedPath.Replace('\\', '/');

            return crossPlatformPath;
        }

        const string packageName = "com.expecto.uml_genertor";
        static ListRequest listRequest;

        void OnEnable()
        {
            if (string.IsNullOrEmpty(outputDirectory))
            {
                outputDirectory = GetCrossPlatformPath(Path.Combine(Application.dataPath, "..", "UML"));

                EditorUtility.SetDirty(this);
                AssetDatabase.SaveAssets();
            }

            if (string.IsNullOrEmpty(generateUMLPath))
            {
                listRequest = Client.List();

                EditorApplication.update += OnUpdate;
            }
        }

        void OnUpdate()
        {
            if (listRequest.IsCompleted)
            {
                if (listRequest.Status == StatusCode.Success)
                {
                    foreach (var package in listRequest.Result)
                    {
                        if (package.name == packageName)
                        {
                            Debug.Log($"Package '{packageName}' is installed.");
                            Debug.Log($"Resolved path: {package.resolvedPath}");
                            generateUMLPath = GetCrossPlatformPath(Path.Combine(package.resolvedPath, "Python", "generate_uml.py"));

                            EditorUtility.SetDirty(this);
                            AssetDatabase.SaveAssets();
                        }
                    }
                }
                else
                {
                    Debug.LogError("Failed to list packages: " + listRequest.Error.message);
                }

                EditorApplication.update -= OnUpdate;
            }
        }
    }

}