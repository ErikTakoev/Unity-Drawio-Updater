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
        public string outputDirectory = "UML";

        [Header("UML Settings")]

        [Tooltip("Automatically clean up classes that no longer exist in the codebase")]
        public bool cleanupClasses = true;

        [Tooltip("Automatically clean up arrows for classes")]
        public bool cleanupArrows = true;

        string GetCrossPlatformPath(string path)
        {
            // Нормалізуємо шлях для поточної ОС
            string normalizedPath = Path.GetFullPath(path);

            string relativePath = Path.GetRelativePath(Application.dataPath + "/../", normalizedPath);

            // Для шляхів, які будуть використовуватися в Python або веб-контексті,
            // можна замінити всі зворотні слеші на прямі
            string crossPlatformPath = relativePath.Replace('\\', '/');

            return crossPlatformPath;
        }

        const string packageName = "com.expecto.drawio-updater";
        static ListRequest listRequest;

        void OnEnable()
        {

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