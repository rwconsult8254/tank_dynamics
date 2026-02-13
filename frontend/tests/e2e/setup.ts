/**
 * Health check to verify backend is running before tests start
 */
async function globalSetup() {
  let retries = 5;
  let lastError: Error | null = null;

  while (retries > 0) {
    try {
      // Use AbortController for proper timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch("http://localhost:8000/api/health", {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        // Give backend a moment to stabilize
        await new Promise((resolve) => setTimeout(resolve, 2000));
        return;
      }

      throw new Error(`Health check returned ${response.status}`);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      retries--;

      if (retries > 0) {
        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
  }

  throw new Error(
    `Backend not running. Start with: uvicorn api.main:app --host 0.0.0.0 --port 8000\n` +
      `Last error: ${lastError?.message}`,
  );
}

export default globalSetup;
