/**
 * Build the URL for an Apex REST endpoint.
 *
 * On an Experience Cloud site the call has to go through the site's path prefix --
 * `/clm/services/apexrest/...` rather than `/services/apexrest/...`. The bare path
 * targets the org's REST API, which does not accept a site session and answers:
 *
 *   [{"message":"This session is not valid for use with the REST API",
 *     "errorCode":"INVALID_SESSION_ID"}]
 *
 * The guest user does not hit this, which is what makes it easy to miss: anonymously the
 * bare path resolves and the endpoint replies normally, and the 401 only appears once
 * someone signs in.
 *
 * Salesforce injects SFDC_ENV.basePath on a site. Off-platform -- a standalone build, a
 * test, the local harness -- there is no prefix and the bare path is correct.
 */
export function apexRestUrl(path: string): string {
  const basePath = (globalThis as { SFDC_ENV?: { basePath?: string } }).SFDC_ENV?.basePath;
  const prefix = basePath ? basePath.replace(/\/+$/, "") : "";
  return `${prefix}${path}`;
}
