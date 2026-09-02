import { render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import { useIntl } from "react-intl";
import { UploadDialog } from "./UploadDialog";

/**
 * Stands in for ContentUploader, which is megabytes of lazy chunk and needs a live Box
 * token. What matters here is the one thing the real element does on mount and this
 * double reproduces exactly: it reads react-intl context, and throws "Could not find
 * required `intl` object" when nothing provides it.
 */
vi.mock("box-ui-elements/es/elements/content-uploader", () => ({
  default: function ContentUploaderDouble() {
    const intl = useIntl();
    return <div data-testid="uploader-double">{intl.locale}</div>;
  },
}));
vi.mock("box-ui-elements/dist/uploader.css", () => ({}));

describe("UploadDialog", () => {
  test("provides the intl context box-ui-elements mounts against", async () => {
    render(<UploadDialog folderId="0" tokenProvider={() => "t"} onClose={() => {}} />);
    // The dialog renders outside BoxElements, so it cannot inherit that provider. Losing
    // this one takes the uploader down at mount, not at upload.
    expect(await screen.findByTestId("uploader-double")).toBeVisible();
  });
});
