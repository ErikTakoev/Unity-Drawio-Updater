using System.Text;
using UnityEditor;
using UnityEngine;

namespace Expecto
{
    public class PythonRunner
    {
        const string LogPrefix = "[PythonRunner] ";

        [MenuItem("Expecto/UML/Generate UML")]
        static void RunGenerateUML()
        {
            var codeAnalyzerSettings = GetSettings<CodeAnalyzerSettings>("t:CodeAnalyzerSettings");
            var umlSettings = GetSettings<UMLSettings>("t:UMLSettings");

            if (codeAnalyzerSettings == null)
            {
                Debug.LogError(LogPrefix + "CodeAnalyzerSettings not found");
                return;
            }
            if (umlSettings == null)
            {
                Debug.LogError(LogPrefix + "UMLSettings not found");
                return;
            }

            RunPythonScript(codeAnalyzerSettings, umlSettings);
        }

        static void RunPythonScript(CodeAnalyzerSettings codeAnalyzerSettings, UMLSettings umlSettings)
        {
            string arguments = $"{umlSettings.generateUMLPath} -i {codeAnalyzerSettings.outputDirectory} -o {umlSettings.outputDirectory}";

            if (umlSettings.cleanupClasses)
            {
                arguments += $" --cleanup-classes";
            }
            if (umlSettings.cleanupArrows)
            {
                arguments += $" --cleanup-arrows";
            }

            Debug.Log(LogPrefix + "Running Python script with arguments: " + arguments);
            System.Diagnostics.ProcessStartInfo start = new System.Diagnostics.ProcessStartInfo();
            start.FileName = umlSettings.pythonPath;
            start.Arguments = arguments;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            start.CreateNoWindow = true;
            start.StandardOutputEncoding = Encoding.UTF8;
            start.StandardErrorEncoding = Encoding.UTF8;

            // Додаємо змінні середовища для UTF-8
            start.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            // Якщо на Windows, встановлюємо додаткові змінні середовища
            if (Application.platform == RuntimePlatform.WindowsEditor)
            {
                start.EnvironmentVariables["PYTHONUTF8"] = "1";
                start.EnvironmentVariables["PYTHONLEGACYWINDOWSSTDIO"] = "0";
            }

            System.Diagnostics.Process process = new System.Diagnostics.Process();
            process.StartInfo = start;

            StringBuilder output = new StringBuilder();
            StringBuilder error = new StringBuilder();

            process.OutputDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                    output.AppendLine(e.Data);
            };

            process.ErrorDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                    error.AppendLine(e.Data);
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            process.WaitForExit();

            Debug.Log(LogPrefix + "Python script output: " + output.ToString());
            if (error.Length > 0)
            {
                Debug.LogError(LogPrefix + "Python script error: " + error.ToString());
            }
        }

        static T GetSettings<T>(string filter) where T : ScriptableObject
        {
            var settings = AssetDatabase.FindAssets(filter);
            if (settings.Length == 0)
            {
                Debug.LogError(LogPrefix + $"{filter} not found");
                return null;
            }
            var path = AssetDatabase.GUIDToAssetPath(settings[0]);
            return AssetDatabase.LoadAssetAtPath<T>(path);
        }
    }
}