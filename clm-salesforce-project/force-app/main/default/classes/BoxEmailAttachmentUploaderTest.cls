@isTest
private class BoxEmailAttachmentUploaderTest {

    private static void assertRoundTrip(String content) {
        Blob mp = BoxEmailAttachmentUploader.buildMultipart('bnd123', 'redline.pdf', '402886371976', Blob.valueOf(content));
        String decoded = mp.toString();
        System.assert(decoded.contains('name="attributes"'), 'attributes part present (len=' + content.length() + ')');
        System.assert(decoded.contains('"parent":{"id":"402886371976"}'), 'attributes reference the folder (len=' + content.length() + ')');
        System.assert(decoded.contains('filename="redline.pdf"'), 'file part names the file (len=' + content.length() + ')');
        System.assert(decoded.contains(content), 'file content preserved byte-exact (len=' + content.length() + '): tail=' + decoded.right(24));
        System.assert(decoded.endsWith('--bnd123--'), 'closing boundary intact (len=' + content.length() + ')');
    }

    @isTest
    static void multipartIsByteExactAcrossAllPaddings() {
        assertRoundTrip('ABCDEF');    // 6 bytes: len % 3 == 0 (no base64 padding)
        assertRoundTrip('ABCDEFG');   // 7 bytes: len % 3 == 1 (base64 '==')
        assertRoundTrip('ABCDEFGH');  // 8 bytes: len % 3 == 2 (base64 '=')
    }

    @isTest
    static void attachmentCarrierHoldsData() {
        BoxEmailAttachmentUploader.Attachment a =
            new BoxEmailAttachmentUploader.Attachment('f.pdf', EncodingUtil.base64Encode(Blob.valueOf('x')));
        System.assertEquals('f.pdf', a.fileName);
        System.assert(String.isNotBlank(a.base64Body), 'base64 body should be set');
    }
}
