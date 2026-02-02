import type { GadgetModel } from "gadget-server";

// This file describes the schema for the "session" model, go to https://course-companion-fte-1.gadget.app/edit to view/edit your model in Gadget
// For more information on how to update this file http://docs.gadget.dev

export const schema: GadgetModel = {
  type: "gadget/model-schema/v2",
  storageKey: "RGViN_DclV9j",
  fields: {
    roles: {
      type: "roleList",
      default: ["unauthenticated"],
      storageKey: "FdR5qRexuq-B",
    },
  },
};
