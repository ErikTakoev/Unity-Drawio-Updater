using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace Expecto.Editor
{
    public static class PythonRunner
    {
        const string LogPrefix = "[PythonRunner] ";

        public static bool LoadSettings(out CodeAnalyzerSettings codeAnalyzerSettings, out UMLSettings umlSettings)
        {
            codeAnalyzerSettings = GetSettings<CodeAnalyzerSettings>("t:CodeAnalyzerSettings");
            umlSettings = GetSettings<UMLSettings>("t:UMLSettings");

            if (codeAnalyzerSettings == null)
            {
                return false;
            }
            if (umlSettings == null)
            {
                return false;
            }

            return true;
        }

        public static string GetArguments(CodeAnalyzerSettings codeAnalyzerSettings, UMLSettings umlSettings)
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
            return arguments;
        }

        public static void RunPythonScript(CodeAnalyzerSettings codeAnalyzerSettings, UMLSettings umlSettings)
        {
            string arguments = GetArguments(codeAnalyzerSettings, umlSettings);

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

        public static T GetSettings<T>(string filter) where T : ScriptableObject
        {
            var settings = AssetDatabase.FindAssets(filter);
            if (settings.Length == 0)
            {
                return null;
            }
            var path = AssetDatabase.GUIDToAssetPath(settings[0]);
            return AssetDatabase.LoadAssetAtPath<T>(path);
        }

    }
}