(function configureTarix360(global) {
  "use strict";

  const hostname = global.location.hostname;
  const isLocalhost = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "";
  const isGitHubPages = hostname.endsWith(".github.io");
  const usesStaticSnapshot = isLocalhost || isGitHubPages;

  // Localhost reads the prepared snapshot. Public deployments request only
  // whitelisted individual files through the serverless Drive gateway.
  global.TARIX360_DEPLOYMENT = Object.freeze({
    environment: isLocalhost ? "localhost" : isGitHubPages ? "github-pages" : "production",
    release: "first15-hybrid-v4",
    contentMode: usesStaticSnapshot ? "local-static" : "drive-api",
    contentEndpoint: "/api/content",
    dataBase: usesStaticSnapshot ? "data" : "",
    mediaManifestPath: isGitHubPages ? "data/media_manifest_github.json" : "data/media_manifest.json",
    assetBase: "",
    bookBase: "",
    sourceOfTruth: "google-drive",
    drive: Object.freeze({
      projectFolderId: "13DOOyIWOgHoNcT8ExWwMb4gow5IMH83n",
      webDatasetFolderId: "12fFMcWf2Go2sDPZC9sTOncKdRuTsH007",
      webMediaFolderId: "1XNFStuw_4nommRfQT8xt-7ixm9dS8oqh",
      bookFolderId: "1Jk0GkISH0nYezMnhnXL3Hnwv-Sc8q9cw",
      bookOriginalFolderId: "1D33KX0ZawPCtbTfj8q4N-xmWs6gA4qrD",
      bookWebPagesFolderId: "1xdgXUBk_QQzPHhP1IfMxyWnwOGwYE8Yo",
      bookOriginalFileId: "1MBVkyq1JJmz3WtFZDjpW4vQeKKoJ2ddY",
      bookPagesManifestFileId: "18-90zh5cLf9N3PvxkCmlahCLf5v26QwY",
      manifestFolderId: "1WBJkOspRPYLXBHTfcaBlGWXPoYtRDDdz",
      webContentManifestFileId: "1Cu_lrZr1J5atKsG-KBnwZkGKjuwa8GuE"
    })
  });
})(window);
