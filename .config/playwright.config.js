import { defineConfig } from "@playwright/test";

const base = defineConfig({
	use: {
		screenshot: "only-on-failure",
		trace: "retain-on-failure",
		permissions: ["clipboard-read", "clipboard-write", "microphone"],
		bypassCSP: true,
		launchOptions: {
			args: [
				"--disable-web-security",
				"--use-fake-device-for-media-stream",
				"--use-fake-ui-for-media-stream",
				"--use-file-for-fake-audio-capture=../gradio/test_data/test_audio.wav"
			]
		}
	},
	expect: { timeout: 15000 },
	timeout: 15000,
	testMatch: /.*.spec.ts/,
	testDir: "..",
	workers: process.env.CI ? 1 : undefined
});

const normal = defineConfig(base, {
	globalSetup: "./playwright-setup.js"
});

normal.projects = undefined; // Explicitly unset this field due to https://github.com/microsoft/playwright/issues/28795

const lite = defineConfig(base, {
	webServer: {
		command: "python -m http.server 8000 --directory ../js/lite",
		url: "http://localhost:8000/",
		reuseExistingServer: !process.env.CI
	},
	testMatch: [
		"**/file_component_events.spec.ts",
		"**/chatbot_multimodal.spec.ts",
		"**/kitchen_sink.spec.ts",
		"**/gallery_component_events.spec.ts"
	],
	workers: 1
});

lite.projects = undefined; // Explicitly unset this field due to https://github.com/microsoft/playwright/issues/28795

export default !!process.env.GRADIO_E2E_TEST_LITE ? lite : normal;
