using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace Expecto.Editor
{
    static class MenuItems
    {
        const string LogPrefix = "[Expecto] ";


        [MenuItem("Expecto/Drawio Diagram/Generate Drawio Diagram", validate = true)]
        static bool ValidateRunGenerateUML()
        {
            CodeAnalyzerSettings codeAnalyzerSettings;
            UMLSettings umlSettings;

            if (!PythonRunner.LoadSettings(out codeAnalyzerSettings, out umlSettings))
            {
                if (codeAnalyzerSettings == null)
                {
                    Debug.LogError(LogPrefix + "CodeAnalyzerSettings not found");
                }
                if (umlSettings == null)
                {
                    Debug.LogError(LogPrefix + "UMLSettings not found");
                }
                return false;
            }
            return true;
        }

        [MenuItem("Expecto/Drawio Diagram/Generate Drawio Diagram", priority = 2, secondaryPriority = 10000)]
        static void RunGenerateUML()
        {
            CodeAnalyzerSettings codeAnalyzerSettings;
            UMLSettings umlSettings;

            if (!PythonRunner.LoadSettings(out codeAnalyzerSettings, out umlSettings))
            {
                return;
            }

            PythonRunner.RunPythonScript(codeAnalyzerSettings, umlSettings);
        }


        [MenuItem("Expecto/Drawio Diagram/Add Git Post Commit Hook", validate = true)]
        static bool ValidateAddGitPostCommitHook()
        {
            CodeAnalyzerSettings codeAnalyzerSettings;
            UMLSettings umlSettings;

            if (!PythonRunner.LoadSettings(out codeAnalyzerSettings, out umlSettings))
            {
                if (codeAnalyzerSettings == null)
                {
                    Debug.LogError(LogPrefix + "CodeAnalyzerSettings not found");
                }
                if (umlSettings == null)
                {
                    Debug.LogError(LogPrefix + "UMLSettings not found");
                }
                return false;
            }

            string hookPath = Application.dataPath + "/../.git/hooks/post-commit";
            return !File.Exists(hookPath);
        }

        [MenuItem("Expecto/Drawio Diagram/Add Git Post Commit Hook", secondaryPriority = 10002)]
        static void AddGitPostCommitHook()
        {
            CodeAnalyzerSettings codeAnalyzerSettings;
            UMLSettings umlSettings;

            if (!PythonRunner.LoadSettings(out codeAnalyzerSettings, out umlSettings))
            {
                return;
            }

            string arguments = PythonRunner.GetArguments(codeAnalyzerSettings, umlSettings);
            string pythonPath = umlSettings.pythonPath;

            string hookPath = Application.dataPath + "/../.git/hooks/post-commit";
            string hookContent =
                "#!/bin/bash\n" +
                "echo 'Git post commit hook started'\n" +
                $"{pythonPath} {arguments}\n" +
                "echo 'Git post commit hook finished'\n";

            File.WriteAllText(hookPath, hookContent);

            Debug.Log(LogPrefix + "Git post commit hook created at " + hookPath);
        }

        [MenuItem("Expecto/Drawio Diagram/Open Settings", validate = true)]
        static bool ValidateOpenSettings()
        {
            CodeAnalyzerSettings codeAnalyzerSettings;
            UMLSettings umlSettings;

            if (!PythonRunner.LoadSettings(out codeAnalyzerSettings, out umlSettings))
            {
                if (codeAnalyzerSettings == null)
                {
                    Debug.LogError(LogPrefix + "CodeAnalyzerSettings not found");
                }
                if (umlSettings == null)
                {
                    Debug.LogError(LogPrefix + "UMLSettings not found");
                }
                return false;
            }

            return true;
        }

        [MenuItem("Expecto/Drawio Diagram/Open Settings", priority = 2, secondaryPriority = 10001)]
        static void OpenSettings()
        {
            var umlSettings = PythonRunner.GetSettings<UMLSettings>("t:UMLSettings");
            Selection.activeObject = umlSettings;
        }

        [MenuItem("Expecto/Drawio Diagram/Create Settings", validate = true)]
        static bool ValidateCreateSettings()
        {
            var codeAnalyzerSettings = PythonRunner.GetSettings<CodeAnalyzerSettings>("t:CodeAnalyzerSettings");
            if (codeAnalyzerSettings == null)
            {
                Debug.LogError(LogPrefix + "CodeAnalyzerSettings not found");
                return false;
            }

            var umlSettings = PythonRunner.GetSettings<UMLSettings>("t:UMLSettings");
            return umlSettings == null;
        }

        [MenuItem("Expecto/Drawio Diagram/Create Settings", secondaryPriority = 10003)]
        static void CreateSettings()
        {
            var umlSettings = ScriptableObject.CreateInstance<UMLSettings>();

            var path = Path.Combine("Assets", "Expecto", "UMLSettings.asset");
            if (!AssetDatabase.IsValidFolder(Path.GetDirectoryName(path)))
            {
                AssetDatabase.CreateFolder("Assets", "Expecto");
            }
            AssetDatabase.CreateAsset(umlSettings, path);
            Selection.activeObject = umlSettings;

            EditorUtility.SetDirty(umlSettings);
            AssetDatabase.SaveAssets();
        }
    }
}