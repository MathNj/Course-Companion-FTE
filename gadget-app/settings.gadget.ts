import type { GadgetSettings } from "gadget-server";

export const settings: GadgetSettings = {
  type: "gadget/settings/v1",
  frameworkVersion: "v1.5.0",
  plugins: {
    connections: {
      chatgpt: {
        // Disable authorization for demo/testing
        // authorizationPath: "/authorize"
      }
    },
  },
};
