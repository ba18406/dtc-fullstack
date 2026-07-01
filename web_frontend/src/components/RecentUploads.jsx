function RecentUploads({ uploads }) {
  return (
    <div className="panel">
      <h3>Recent Uploads</h3>

      <ul className="upload-list">
        {uploads.length === 0 ? (
          <li>No uploads found.</li>
        ) : (
          uploads.map((item, index) => (
            <li key={index}>
              <strong>{item.file_name}</strong>
              <span>{item.username}</span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default RecentUploads;