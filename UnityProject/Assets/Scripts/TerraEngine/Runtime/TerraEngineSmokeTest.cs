
using UnityEngine;

namespace AetherEngine.TerraEngine
{
    public class TerraEngineSmokeTest : MonoBehaviour
    {
        private TerraEngineRuntime runtime;

        private void Start()
        {
            try
            {
                Debug.Log("================================");
                Debug.Log("AetherEngine: TerraEngine Test");
                Debug.Log("================================");

                string version = TerraEngineRuntime.GetAPIVersion();

                Debug.Log($"TerraEngine API Version: {version}");

                runtime = new TerraEngineRuntime();

                Debug.Log("TerraEngine native runtime created successfully!");
            }
            catch (System.Exception exception)
            {
                Debug.LogError(
                    $"TerraEngine initialization failed:\n{exception}"
                );
            }
        }

        private void OnDestroy()
        {
            if (runtime == null)
                return;

            try
            {
                runtime.Dispose();
                Debug.Log("TerraEngine native runtime destroyed.");
            }
            catch (System.Exception exception)
            {
                Debug.LogError(
                    $"TerraEngine shutdown failed:\n{exception}"
                );
            }

            runtime = null;
        }
    }
}
