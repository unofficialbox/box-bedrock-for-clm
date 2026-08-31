import { afterEach, describe, expect, test } from "vitest";
import { apexRestUrl } from "./apexRest";

/**
 * The bare path works for the guest user and fails for a signed-in one with
 * INVALID_SESSION_ID, so this is pinned: the difference is invisible until someone logs
 * in, which is exactly when a demo is being given.
 */
describe("Apex REST URLs", () => {
  afterEach(() => {
    delete (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV;
  });

  test("routes through the Experience Cloud site prefix", () => {
    (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV = { basePath: "/clm" };
    expect(apexRestUrl("/services/apexrest/clm/box-token?recordId=a01")).toBe(
      "/clm/services/apexrest/clm/box-token?recordId=a01",
    );
  });

  test("tolerates a trailing slash on the prefix", () => {
    (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV = { basePath: "/clm/" };
    expect(apexRestUrl("/services/apexrest/clm/contracts")).toBe("/clm/services/apexrest/clm/contracts");
  });

  test("leaves the path alone off-platform, where the local harness serves it", () => {
    expect(apexRestUrl("/services/apexrest/clm/contracts")).toBe("/services/apexrest/clm/contracts");
  });
})
