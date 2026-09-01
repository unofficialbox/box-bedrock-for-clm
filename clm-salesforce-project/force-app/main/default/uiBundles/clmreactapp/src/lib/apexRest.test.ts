import { afterEach, describe, expect, test } from "vitest";
import { apexRestUrl } from "./apexRest";

/**
 * Pinned because two plausible-looking URLs are both wrong against a signed-in session,
 * and one of them fails silently:
 *
 *   /services/apexrest/...      401 INVALID_SESSION_ID
 *   /clm/services/apexrest/...  200 with the SPA shell
 *
 * Only SFDC_ENV.apiPath reaches Apex.
 */
describe("Apex REST URLs", () => {
  afterEach(() => {
    delete (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV;
  });

  test("goes through the bundle's apiPath", () => {
    (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV = { apiPath: "/clm/sf/api", basePath: "/clm" };
    expect(apexRestUrl("/services/apexrest/clm/box-token?recordId=a01")).toBe(
      "/clm/sf/api/services/apexrest/clm/box-token?recordId=a01",
    );
  });

  test("does not use the site path, which serves the app rather than Apex", () => {
    (globalThis as { SFDC_ENV?: unknown }).SFDC_ENV = { apiPath: "/clm/sf/api", basePath: "/clm" };
    expect(apexRestUrl("/services/apexrest/clm/contracts")).not.toBe(
      "/clm/services/apexrest/clm/contracts",
    );
  });

  test("leaves the path alone off-platform, where the local harness serves it", () => {
    expect(apexRestUrl("/services/apexrest/clm/contracts")).toBe("/services/apexrest/clm/contracts");
  });
});
