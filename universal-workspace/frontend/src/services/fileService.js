import api from "../api/axios";

// ============================================================
// UPLOAD FILE
// ============================================================

export const uploadFile = async (file) => {
  const formData = new FormData();

  formData.append("upload_file", file);

  const response = await api.post(
    "/files/upload",
    formData
  );

  return response.data;
};


// ============================================================
// GET MY FILES
// ============================================================

export const getMyFiles = async ({
  page = 1,
  limit = 10,
  search = "",
  file_type = "",
  mime_type = "",
} = {}) => {
  const response = await api.get("/files/", {
    params: {
      page,
      limit,
      search: search || undefined,
      file_type: file_type || undefined,
      mime_type: mime_type || undefined,
    },
  });

  return response.data;
};


// ============================================================
// DOWNLOAD FILE
// ============================================================

export const downloadFile = async (fileId) => {
  const response = await api.get(
    `/files/${fileId}/download`,
    {
      responseType: "blob",
    }
  );

  return response;
};


// ============================================================
// PREVIEW FILE
// ============================================================ 
export const previewFile = async (fileId) => {
  const response = await api.get(
    `/files/${fileId}/preview`,
    {
      responseType: "blob",
    }
  );

  return response;
};


// ============================================================
// RENAME FILE
// ============================================================

export const renameFile = async (
  fileId,
  filename
) => {
  const response = await api.patch(
    `/files/${fileId}/rename`,
    {
      filename,
    }
  );

  return response.data;
};


// ============================================================
// DELETE FILE
// ============================================================

export const deleteFile = async (fileId) => {
  const response = await api.delete(
    `/files/${fileId}`
  );

  return response.data;
};


// ============================================================
// CREATE SHARE LINK
// ============================================================

export const shareFile = async (fileId) => {
  const response = await api.post(
    `/files/${fileId}/share`
  );

  return response.data;
};


// ============================================================
// REVOKE SHARE LINK
// ============================================================

export const revokeShare = async (fileId) => {
  const response = await api.delete(
    `/files/${fileId}/share`
  );

  return response.data;
};