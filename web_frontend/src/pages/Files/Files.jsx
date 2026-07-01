import { useEffect, useState } from "react";
import { getCurrentUser } from "../../services/authService";
import {
  getVisibleFiles,
  uploadFile,
  getDownloadUrl,
  deleteFile,
} from "../../services/fileService";
import "../../styles/dashboard.css";
import "../../styles/users.css";
import { addActivityLog } from "../../services/logService";

function Files() {
  const currentUser = getCurrentUser();
  const user = currentUser?.user || currentUser;

  const [files, setFiles] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  async function loadFiles() {
    try {
      const data = await getVisibleFiles(user.id, user.role, user.username);

      if (data.success) {
        setFiles(data.files);
      } else {
        alert(data.error || "Unable to load files.");
      }
    } catch (err) {
      console.error(err);
      alert("API error while loading files.");
    }
  }

  async function handleUpload() {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    try {
      setUploading(true);

      const result = await uploadFile(selectedFile, user.id);

      if (result.success) {

          await addActivityLog(
              user.id,
              "UPLOAD",
              selectedFile.name
          );

          alert("File uploaded successfully.");

          setSelectedFile(null);

          await loadFiles();
      }else {
        alert(result.error || "Upload failed.");
      }
    } catch (err) {
      console.error(err);
      alert("API error while uploading file.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(item) {

      await addActivityLog(
          user.id,
          "DOWNLOAD",
          item.file_name
      );

      window.open(
          getDownloadUrl(item.id),
          "_blank"
      );

  }

  async function handleDelete(item) {
    const confirmed = window.confirm(
      `Are you sure you want to delete this file?\n\n${item.file_name}`
    );

    if (!confirmed) return;

    try {
      const result = await deleteFile(
        item.id,
        user.id,
        user.role,
        user.username
      );

    if (result.success) {

        await addActivityLog(
            user.id,
            "DELETE",
            item.file_name
        );

        alert("File deleted successfully.");

        await loadFiles();

    }else {
        alert(result.error || "Delete failed.");
      }
    } catch (err) {
      console.error(err);
      alert("API error while deleting file.");
    }
  }

  async function handlePreview(item) {

      await addActivityLog(
          user.id,
          "PREVIEW",
          item.file_name
      );

      setPreviewFile(item);

      setShowPreview(true);

  }

  function getFileExtension(fileName) {
    return fileName.split(".").pop().toLowerCase();
  }

  useEffect(() => {
    if (user?.id && user?.role && user?.username) {
      loadFiles();
    }
  }, []);

  const filteredFiles = files.filter((item) => {
    const text = `
      ${item.file_name}
      ${item.file_type}
      ${item.uploaded_by}
      ${item.uploaded_at}
    `.toLowerCase();

    return text.includes(searchText.toLowerCase());
  });

  return (
    <div className="dashboard-page">
      <div className="page-title">
        <h1>Files Management</h1>
        <p>Upload, preview, download and manage files</p>
      </div>

      <div className="users-toolbar">
        <input
          type="text"
          placeholder="Search files..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />

        <div className="files-actions">
          <input
            type="file"
            onChange={(e) => setSelectedFile(e.target.files[0])}
            disabled={uploading}
          />

          <button className="primary-btn" onClick={handleUpload} disabled={uploading}>
            {uploading ? "Uploading..." : "Upload File"}
          </button>

          <button className="secondary-btn" onClick={loadFiles} disabled={uploading}>
            Refresh
          </button>
        </div>
      </div>

      <div className="panel">
        <h3>Visible Files</h3>

        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>File Name</th>
              <th>Type</th>
              <th>Path</th>
              <th>Uploaded By</th>
              <th>Upload Date</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredFiles.length === 0 ? (
              <tr>
                <td colSpan="7">No files found.</td>
              </tr>
            ) : (
              filteredFiles.map((item) => (
                <tr key={item.id} onDoubleClick={() => handlePreview(item)}>
                  <td>{item.id}</td>
                  <td>{item.file_name}</td>
                  <td>{item.file_type}</td>
                  <td>{item.file_path}</td>
                  <td>{item.uploaded_by}</td>
                  <td>{item.uploaded_at}</td>
                  <td>
                    <button className="table-btn" onClick={() => handlePreview(item)}>
                      Preview
                    </button>

                    <button className="table-btn" onClick={() => handleDownload(item)}>
                      Download
                    </button>

                    <button className="table-btn danger" onClick={() => handleDelete(item)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showPreview && previewFile && (
        <div className="modal-overlay">
          <div className="file-preview-modal">
            <div className="preview-header">
              <h2>{previewFile.file_name}</h2>

              <button className="secondary-btn" onClick={() => setShowPreview(false)}>
                Close
              </button>
            </div>

            <div className="preview-body">
              {["png", "jpg", "jpeg", "gif", "bmp", "webp"].includes(
                getFileExtension(previewFile.file_name)
              ) && (
                <img
                  src={getDownloadUrl(previewFile.id)}
                  alt={previewFile.file_name}
                  className="preview-image"
                />
              )}

              {getFileExtension(previewFile.file_name) === "pdf" && (
                <iframe
                  src={getDownloadUrl(previewFile.id)}
                  title="PDF Preview"
                  className="preview-frame"
                />
              )}

              {["doc", "docx", "xls", "xlsx"].includes(
                getFileExtension(previewFile.file_name)
              ) && (
                <div className="preview-message">
                  <h3>Preview not supported directly in browser</h3>
                  <p>
                    Word and Excel files usually need to be opened with Microsoft
                    Office, Google Docs, or downloaded first.
                  </p>

                  <button
                    className="primary-btn"
                    onClick={() => handleDownload(previewFile)}
                  >
                    Open / Download File
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Files;