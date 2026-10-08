import { useEffect, useState } from "react";
import api from "../api/axios";

import {
    uploadFile,
    getMyFiles,
    downloadFile,
    renameFile,
    deleteFile,
    shareFile,
    revokeShare,
    previewFile,
} from "../services/fileService";

import { processFile } from "../services/processingService";


// ============================================================
// FILE CATEGORY HELPER
// ============================================================

const getFileCategory = (file) => {
    const mimeType = (file?.mime_type || "").toLowerCase();
    const filename = (
        file?.filename ||
        file?.original_filename ||
        ""
    ).toLowerCase();

    if (mimeType.startsWith("image/")) {
        return "image";
    }

    if (mimeType === "application/pdf" || filename.endsWith(".pdf")) {
        return "pdf";
    }

    if (
        mimeType.startsWith("audio/") ||
        /\.(mp3|wav|ogg|m4a|aac|flac)$/i.test(filename)
    ) {
        return "audio";
    }

    if (
        mimeType.startsWith("video/") ||
        /\.(mp4|avi|mov|mkv|webm|m4v)$/i.test(filename)
    ) {
        return "video";
    }

    if (
        mimeType.startsWith("text/") ||
        mimeType.includes("word") ||
        mimeType.includes("document") ||
        mimeType.includes("officedocument") ||
        /\.(doc|docx|txt|rtf|odt)$/i.test(filename)
    ) {
        return "document";
    }

    return "other";
};


// ============================================================
// PROCESSING OPERATIONS
// ============================================================

const processingOperations = {
    image: [
        {
            value: "compress",
            label: "Compress",
        },
        {
            value: "convert",
            label: "Convert",
        },
        {
            value: "resize",
            label: "Resize",
        },
        {
            value: "crop",
            label: "Crop",
        },
    ],

    pdf: [
        {
            value: "compress",
            label: "Compress",
        },
        {
            value: "convert",
            label: "Convert",
        },
    ],

    document: [
        {
            value: "convert",
            label: "Convert",
        },
        {
            value: "compress",
            label: "Compress",
        },
    ],

    audio: [
        {
            value: "compress",
            label: "Compress",
        },
        {
            value: "convert",
            label: "Convert",
        },
    ],

    video: [
        {
            value: "compress",
            label: "Compress",
        },
        {
            value: "convert",
            label: "Convert",
        },
        {
            value: "resize",
            label: "Resize",
        },
    ],
};


// ============================================================
// DEFAULT OPTIONS
// ============================================================

const getDefaultOptions = (category, operation) => {
    if (operation === "compress") {
        return {
            quality: 70,
        };
    }

    if (operation === "convert") {
        if (category === "image") {
            return {
                format: "jpg",
            };
        }

        if (category === "audio") {
            return {
                format: "mp3",
            };
        }

        if (category === "video") {
            return {
                format: "mp4",
            };
        }

        if (category === "document") {
            return {
                format: "pdf",
            };
        }

        if (category === "pdf") {
            return {
                format: "pdf",
            };
        }
    }

    if (operation === "resize") {
        return {
            width: 800,
            height: 600,
        };
    }

    if (operation === "crop") {
        return {
            left: 0,
            top: 0,
            right: 800,
            bottom: 600,
        };
    }

    return {};
};


// ============================================================
// DASHBOARD
// ============================================================

function Dashboard({ onLogout }) {
    const [user, setUser] = useState(null);


    // ============================================================
    // UPLOAD
    // ============================================================

    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);


    // ============================================================
    // FILES
    // ============================================================

    const [files, setFiles] = useState([]);
    const [filesLoading, setFilesLoading] = useState(false);


    // ============================================================
    // SEARCH
    // ============================================================

    const [search, setSearch] = useState("");


    // ============================================================
    // FILTER
    // ============================================================

    const [fileType, setFileType] = useState("");


    // ============================================================
    // PAGINATION
    // ============================================================

    const [page, setPage] = useState(1);
    const [limit] = useState(5);

    const [pagination, setPagination] = useState({
        page: 1,
        limit: 5,
        total: 0,
        total_pages: 1,
    });


    // ============================================================
    // RENAME
    // ============================================================

    const [renamingFileId, setRenamingFileId] = useState(null);
    const [newFilename, setNewFilename] = useState("");
    const [renaming, setRenaming] = useState(false);


    // ============================================================
    // DELETE
    // ============================================================

    const [deletingFileId, setDeletingFileId] = useState(null);


    // ============================================================
    // SHARE
    // ============================================================

    const [sharingFileId, setSharingFileId] = useState(null);
    const [sharedLinks, setSharedLinks] = useState({});


    // ============================================================
    // PROCESSING
    // ============================================================

    const [processingFileId, setProcessingFileId] = useState("");
    const [processingCategory, setProcessingCategory] = useState("");
    const [processingOperation, setProcessingOperation] =
        useState("");
    const [processingOptions, setProcessingOptions] = useState({});
    const [processing, setProcessing] = useState(false);
    const [processedResult, setProcessedResult] = useState(null);


    // ============================================================
    // MESSAGES
    // ============================================================

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");


    // ============================================================
    // LOAD USER
    // ============================================================

    useEffect(() => {
        const loadUser = async () => {
            try {
                const response = await api.get("/auth/me");

                setUser(response.data);
            } catch (err) {
                console.error(
                    "Failed to load user:",
                    err
                );

                setError(
                    err.response?.data?.detail ||
                    "Failed to load user information"
                );
            }
        };

        loadUser();
    }, []);


    // ============================================================
    // LOAD FILES
    // ============================================================

    const loadFiles = async (
        pageValue = page,
        searchValue = search,
        fileTypeValue = fileType
    ) => {
        setFilesLoading(true);

        try {
            const data = await getMyFiles({
                page: pageValue,
                limit,
                search: searchValue,
                file_type: fileTypeValue,
            });

            console.log("Files response:", data);

            setFiles(data.items || []);

            setPagination(
                data.pagination || {
                    page: pageValue,
                    limit,
                    total: 0,
                    total_pages: 1,
                }
            );
        } catch (err) {
            console.error(
                "Failed to load files:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to load files"
            );
        } finally {
            setFilesLoading(false);
        }
    };


    // ============================================================
    // LOAD FILES AFTER USER
    // ============================================================

    useEffect(() => {
        if (user) {
            loadFiles(1, "", "");
        }
    }, [user]);


    // ============================================================
    // FILE SELECT
    // ============================================================

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];

        setMessage("");
        setError("");

        if (!file) {
            setSelectedFile(null);
            return;
        }

        setSelectedFile(file);
    };


    // ============================================================
    // UPLOAD
    // ============================================================

    const handleUpload = async () => {
        if (!selectedFile) {
            setError(
                "Please select a file first."
            );

            return;
        }

        setUploading(true);
        setMessage("");
        setError("");

        try {
            const data =
                await uploadFile(selectedFile);

            console.log(
                "Upload response:",
                data
            );

            setMessage(
                "File uploaded successfully!"
            );

            setSelectedFile(null);

            const fileInput =
                document.getElementById(
                    "file-upload"
                );

            if (fileInput) {
                fileInput.value = "";
            }

            setPage(1);

            await loadFiles(
                1,
                search,
                fileType
            );
        } catch (err) {
            console.error(
                "Upload error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "File upload failed"
            );
        } finally {
            setUploading(false);
        }
    };


    // ============================================================
    // DOWNLOAD
    // ============================================================

    const handleDownload = async (file) => {
        try {
            setError("");
            setMessage("");

            const response =
                await downloadFile(file.id);

            const blob = new Blob(
                [response.data],
                {
                    type: file.mime_type,
                }
            );

            const url =
                window.URL.createObjectURL(
                    blob
                );

            const link =
                document.createElement("a");

            link.href = url;

            link.download =
                file.filename ||
                file.original_filename ||
                "download";

            document.body.appendChild(link);

            link.click();

            link.remove();

            window.URL.revokeObjectURL(
                url
            );
        } catch (err) {
            console.error(
                "Download error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to download file"
            );
        }
    };


    // ============================================================
    // PREVIEW
    // ============================================================

    const handlePreview = async (file) => {
        try {
            setError("");

            const response =
                await previewFile(file.id);

            const blob = new Blob(
                [response.data],
                {
                    type: file.mime_type,
                }
            );

            const url =
                window.URL.createObjectURL(
                    blob
                );

            window.open(
                url,
                "_blank"
            );

            setTimeout(() => {
                window.URL.revokeObjectURL(
                    url
                );
            }, 1000);
        } catch (err) {
            console.error(
                "Preview error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to preview file"
            );
        }
    };


    // ============================================================
    // START RENAME
    // ============================================================

    const startRename = (file) => {
        setError("");
        setMessage("");

        setRenamingFileId(file.id);

        setNewFilename(
            file.filename ||
            file.original_filename ||
            ""
        );
    };


    // ============================================================
    // CANCEL RENAME
    // ============================================================

    const cancelRename = () => {
        setRenamingFileId(null);
        setNewFilename("");
        setError("");
    };


    // ============================================================
    // RENAME
    // ============================================================

    const handleRename = async (file) => {
        const filename =
            newFilename.trim();

        if (!filename) {
            setError(
                "Please enter a filename."
            );

            return;
        }

        setRenaming(true);
        setError("");
        setMessage("");

        try {
            const data =
                await renameFile(
                    file.id,
                    filename
                );

            console.log(
                "Rename response:",
                data
            );

            setMessage(
                "File renamed successfully!"
            );

            setRenamingFileId(null);
            setNewFilename("");

            await loadFiles(
                page,
                search,
                fileType
            );
        } catch (err) {
            console.error(
                "Rename error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to rename file"
            );
        } finally {
            setRenaming(false);
        }
    };


    // ============================================================
    // SHARE
    // ============================================================

    const handleShare = async (file) => {
        setSharingFileId(file.id);
        setError("");
        setMessage("");

        try {
            const data =
                await shareFile(file.id);

            console.log(
                "Share response:",
                data
            );

            const shareUrl =
                data.share_url ||
                data.url ||
                data.link;

            setSharedLinks(
                (previous) => ({
                    ...previous,
                    [file.id]: shareUrl,
                })
            );

            setMessage(
                "File shared successfully!"
            );
        } catch (err) {
            console.error(
                "Share error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to share file"
            );
        } finally {
            setSharingFileId(null);
        }
    };


    // ============================================================
    // REVOKE SHARE
    // ============================================================

    const handleRevokeShare = async (file) => {
        try {
            setError("");
            setMessage("");

            await revokeShare(file.id);

            setSharedLinks(
                (previous) => {
                    const updated = {
                        ...previous,
                    };

                    delete updated[file.id];

                    return updated;
                }
            );

            setMessage(
                "Share link revoked successfully!"
            );
        } catch (err) {
            console.error(
                "Revoke share error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to revoke share link"
            );
        }
    };


    // ============================================================
    // DELETE
    // ============================================================

    const handleDelete = async (file) => {
        const filename =
            file.filename ||
            file.original_filename ||
            "this file";

        const confirmed =
            window.confirm(
                `Are you sure you want to delete "${filename}"?`
            );

        if (!confirmed) {
            return;
        }

        setDeletingFileId(file.id);
        setError("");
        setMessage("");

        try {
            const data =
                await deleteFile(file.id);

            console.log(
                "Delete response:",
                data
            );

            setMessage(
                "File deleted successfully!"
            );

            await loadFiles(
                page,
                search,
                fileType
            );
        } catch (err) {
            console.error(
                "Delete error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to delete file"
            );
        } finally {
            setDeletingFileId(null);
        }
    };


    // ============================================================
    // SEARCH
    // ============================================================

    const handleSearch = async (e) => {
        e.preventDefault();

        setError("");
        setMessage("");

        setPage(1);

        await loadFiles(
            1,
            search,
            fileType
        );
    };


    // ============================================================
    // CLEAR SEARCH
    // ============================================================

    const handleClearSearch = async () => {
        setSearch("");

        setError("");
        setMessage("");

        setPage(1);

        await loadFiles(
            1,
            "",
            fileType
        );
    };


    // ============================================================
    // FILE TYPE FILTER
    // ============================================================

    const handleFileTypeChange = async (e) => {
        const value =
            e.target.value;

        setFileType(value);

        setError("");
        setMessage("");

        setPage(1);

        await loadFiles(
            1,
            search,
            value
        );
    };


    // ============================================================
    // CLEAR FILTERS
    // ============================================================

    const handleClearFilters = async () => {
        setSearch("");
        setFileType("");
        setPage(1);

        setError("");
        setMessage("");

        await loadFiles(
            1,
            "",
            ""
        );
    };


    // ============================================================
    // PAGINATION
    // ============================================================

    const handlePreviousPage = async () => {
        if (page <= 1) {
            return;
        }

        const newPage =
            page - 1;

        setPage(newPage);

        await loadFiles(
            newPage,
            search,
            fileType
        );
    };


    const handleNextPage = async () => {
        if (
            page >=
            pagination.total_pages
        ) {
            return;
        }

        const newPage =
            page + 1;

        setPage(newPage);

        await loadFiles(
            newPage,
            search,
            fileType
        );
    };


    // ============================================================
    // PROCESSING FILE SELECT
    // ============================================================

    const handleProcessingFileChange = (e) => {
        const fileId =
            e.target.value;

        setProcessingFileId(fileId);

        setProcessedResult(null);
        setError("");
        setMessage("");

        if (!fileId) {
            setProcessingCategory("");
            setProcessingOperation("");
            setProcessingOptions({});

            return;
        }

        const file =
            files.find(
                (item) =>
                    String(item.id) ===
                    String(fileId)
            );

        if (!file) {
            return;
        }

        const category =
            getFileCategory(file);

        setProcessingCategory(
            category
        );

        const operations =
            processingOperations[
                category
            ] || [];

        const firstOperation =
            operations[0]?.value || "";

        setProcessingOperation(
            firstOperation
        );

        setProcessingOptions(
            getDefaultOptions(
                category,
                firstOperation
            )
        );
    };


    // ============================================================
    // PROCESSING OPERATION CHANGE
    // ============================================================

    const handleProcessingOperationChange = (
        e
    ) => {
        const newOperation =
            e.target.value;

        setProcessingOperation(
            newOperation
        );

        setProcessingOptions(
            getDefaultOptions(
                processingCategory,
                newOperation
            )
        );

        setProcessedResult(null);
        setError("");
    };


    // ============================================================
    // PROCESSING OPTION CHANGE
    // ============================================================

    const updateProcessingOption = (
        key,
        value
    ) => {
        setProcessingOptions(
            (previous) => ({
                ...previous,
                [key]: value,
            })
        );
    };


    // ============================================================
    // PROCESS FILE
    // ============================================================

    const handleProcess = async () => {
        if (!processingFileId) {
            setError(
                "Please select a file to process."
            );

            return;
        }

        if (!processingOperation) {
            setError(
                "Please select a processing operation."
            );

            return;
        }

        const file =
            files.find(
                (item) =>
                    String(item.id) ===
                    String(processingFileId)
            );

        if (!file) {
            setError(
                "Selected file was not found."
            );

            return;
        }

        setProcessing(true);
        setError("");
        setMessage("");
        setProcessedResult(null);

        try {
            console.log(
                "Processing:",
                {
                    fileId: file.id,
                    category:
                        processingCategory,
                    operation:
                        processingOperation,
                    options:
                        processingOptions,
                }
            );

            const result =
                await processFile(
                    file.id,
                    processingOperation,
                    processingOptions
                );

            console.log(
                "Processing response:",
                result
            );

            setProcessedResult(
                result
            );

            setMessage(
                "File processed successfully!"
            );

            // Refresh file list so
            // processed file appears
            await loadFiles(
                page,
                search,
                fileType
            );
        } catch (err) {
            console.error(
                "Processing error:",
                err
            );

            setError(
                err.response?.data?.detail ||
                "Failed to process file"
            );
        } finally {
            setProcessing(false);
        }
    };


    // ============================================================
    // RESET PROCESSING
    // ============================================================

    const resetProcessing = () => {
        setProcessingFileId("");
        setProcessingCategory("");
        setProcessingOperation("");
        setProcessingOptions({});
        setProcessedResult(null);
        setProcessing(false);
    };


    // ============================================================
    // ERROR / LOADING
    // ============================================================

    if (error && !user) {
        return (
            <div>
                <h1>Dashboard</h1>

                <p>{error}</p>

                <button
                    type="button"
                    onClick={onLogout}
                >
                    Logout
                </button>
            </div>
        );
    }


    if (!user) {
        return (
            <p>
                Loading dashboard...
            </p>
        );
    }


    // ============================================================
    // CURRENT PROCESSING OPERATIONS
    // ============================================================

    const availableProcessingOperations =
        processingOperations[
            processingCategory
        ] || [];


    // ============================================================
    // DASHBOARD
    // ============================================================

    return (
        <div>
            <h1>
                Universal Workspace
            </h1>

            <h2>
                Dashboard
            </h2>


            {/* ========================================================
                USER INFORMATION
            ======================================================== */}

            <p>
                Welcome,{" "}
                <strong>
                    {user.name}
                </strong>
                !
            </p>

            <p>
                Email: {user.email}
            </p>

            <p>
                User ID: {user.id}
            </p>

            <p>
                Status:{" "}
                {user.is_active
                    ? "Active"
                    : "Inactive"}
            </p>


            <hr />


            {/* ========================================================
                UPLOAD
            ======================================================== */}

            <h3>
                Upload File
            </h3>

            <input
                id="file-upload"
                type="file"
                onChange={
                    handleFileChange
                }
            />

            {selectedFile && (
                <p>
                    Selected file:{" "}
                    <strong>
                        {selectedFile.name}
                    </strong>
                </p>
            )}

            <button
                type="button"
                onClick={
                    handleUpload
                }
                disabled={
                    !selectedFile ||
                    uploading
                }
            >
                {uploading
                    ? "Uploading..."
                    : "Upload File"}
            </button>


            {message && (
                <p>
                    {message}
                </p>
            )}

            {error && user && (
                <p>
                    {error}
                </p>
            )}


            <hr />


            {/* ========================================================
                MY FILES
            ======================================================== */}

            <h3>
                My Files
            </h3>


            {/* SEARCH */}

            <form
                onSubmit={
                    handleSearch
                }
            >
                <input
                    type="text"
                    placeholder="Search files..."
                    value={search}
                    onChange={(e) =>
                        setSearch(
                            e.target.value
                        )
                    }
                />

                <button type="submit">
                    Search
                </button>

                <button
                    type="button"
                    onClick={
                        handleClearSearch
                    }
                >
                    Clear Search
                </button>
            </form>


            <br />


            {/* FILE TYPE FILTER */}

            <label>
                File Type:{" "}

                <select
                    value={fileType}
                    onChange={
                        handleFileTypeChange
                    }
                >
                    <option value="">
                        All Files
                    </option>

                    <option value="image">
                        Images
                    </option>

                    <option value="document">
                        Documents
                    </option>

                    <option value="pdf">
                        PDF
                    </option>

                    <option value="audio">
                        Audio
                    </option>

                    <option value="video">
                        Video
                    </option>

                    <option value="text">
                        Text
                    </option>
                </select>
            </label>


            <button
                type="button"
                onClick={
                    handleClearFilters
                }
            >
                Clear Filters
            </button>


            <br />
            <br />


            {/* ========================================================
                FILE LIST
            ======================================================== */}

            {filesLoading ? (
                <p>
                    Loading files...
                </p>
            ) : files.length === 0 ? (
                <p>
                    {search ||
                    fileType
                        ? "No files found."
                        : "No files uploaded yet."}
                </p>
            ) : (
                <div>
                    {files.map(
                        (file) => (
                            <div
                                key={
                                    file.id
                                }
                            >
                                <hr />

                                {/* FILE NAME */}

                                {renamingFileId ===
                                file.id ? (
                                    <div>
                                        <input
                                            type="text"
                                            value={
                                                newFilename
                                            }
                                            onChange={(
                                                e
                                            ) =>
                                                setNewFilename(
                                                    e.target
                                                        .value
                                                )
                                            }
                                            disabled={
                                                renaming
                                            }
                                        />

                                        <button
                                            type="button"
                                            onClick={() =>
                                                handleRename(
                                                    file
                                                )
                                            }
                                            disabled={
                                                renaming
                                            }
                                        >
                                            {renaming
                                                ? "Saving..."
                                                : "Save"}
                                        </button>

                                        <button
                                            type="button"
                                            onClick={
                                                cancelRename
                                            }
                                            disabled={
                                                renaming
                                            }
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                ) : (
                                    <p>
                                        <strong>
                                            {file.filename ||
                                                file.original_filename}
                                        </strong>
                                    </p>
                                )}


                                {/* FILE INFORMATION */}

                                <p>
                                    Category:{" "}
                                    {getFileCategory(
                                        file
                                    )}
                                </p>

                                <p>
                                    Type:{" "}
                                    {
                                        file.mime_type
                                    }
                                </p>

                                <p>
                                    Size:{" "}
                                    {
                                        file.file_size
                                    }{" "}
                                    bytes
                                </p>

                                <p>
                                    Uploaded:{" "}
                                    {
                                        file.created_at
                                    }
                                </p>


                                {/* ACTIONS */}

                                <button
                                    type="button"
                                    onClick={() =>
                                        handleDownload(
                                            file
                                        )
                                    }
                                >
                                    Download
                                </button>


                                <button
                                    type="button"
                                    onClick={() =>
                                        handlePreview(
                                            file
                                        )
                                    }
                                >
                                    Preview
                                </button>


                                <button
                                    type="button"
                                    onClick={() =>
                                        handleShare(
                                            file
                                        )
                                    }
                                    disabled={
                                        sharingFileId ===
                                        file.id
                                    }
                                >
                                    {sharingFileId ===
                                    file.id
                                        ? "Sharing..."
                                        : "Share"}
                                </button>


                                {sharedLinks[
                                    file.id
                                ] && (
                                    <div>
                                        <p>
                                            Share Link:
                                        </p>

                                        <a
                                            href={
                                                sharedLinks[
                                                    file.id
                                                ]
                                            }
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {
                                                sharedLinks[
                                                    file.id
                                                ]
                                            }
                                        </a>

                                        <br />

                                        <button
                                            type="button"
                                            onClick={() =>
                                                handleRevokeShare(
                                                    file
                                                )
                                            }
                                        >
                                            Revoke Share
                                        </button>
                                    </div>
                                )}


                                {renamingFileId !==
                                    file.id && (
                                    <button
                                        type="button"
                                        onClick={() =>
                                            startRename(
                                                file
                                            )
                                        }
                                    >
                                        Rename
                                    </button>
                                )}


                                <button
                                    type="button"
                                    onClick={() =>
                                        handleDelete(
                                            file
                                        )
                                    }
                                    disabled={
                                        deletingFileId ===
                                        file.id
                                    }
                                >
                                    {deletingFileId ===
                                    file.id
                                        ? "Deleting..."
                                        : "Delete"}
                                </button>
                            </div>
                        )
                    )}
                </div>
            )}


            {/* ========================================================
                PAGINATION
            ======================================================== */}

            {pagination.total_pages >
                1 && (
                <div>
                    <hr />

                    <p>
                        Page{" "}
                        <strong>
                            {page}
                        </strong>{" "}
                        of{" "}
                        <strong>
                            {
                                pagination.total_pages
                            }
                        </strong>
                    </p>

                    <p>
                        Total files:{" "}
                        {
                            pagination.total
                        }
                    </p>

                    <button
                        type="button"
                        onClick={
                            handlePreviousPage
                        }
                        disabled={
                            page <= 1 ||
                            filesLoading
                        }
                    >
                        Previous
                    </button>

                    <button
                        type="button"
                        onClick={
                            handleNextPage
                        }
                        disabled={
                            page >=
                                pagination.total_pages ||
                            filesLoading
                        }
                    >
                        Next
                    </button>
                </div>
            )}


            <hr />


            {/* ========================================================
                FILE PROCESSING
            ======================================================== */}

            <h3>
                File Processing
            </h3>

            <p>
                Select a file and choose
                the operation you want.
            </p>


            {/* SELECT FILE */}

            <div>
                <label>
                    File:{" "}

                    <select
                        value={
                            processingFileId
                        }
                        onChange={
                            handleProcessingFileChange
                        }
                    >
                        <option value="">
                            Select a file
                        </option>

                        {files
                            .filter(
                                (file) =>
                                    processingOperations[
                                        getFileCategory(
                                            file
                                        )
                                    ]
                            )
                            .map(
                                (file) => (
                                    <option
                                        key={
                                            file.id
                                        }
                                        value={
                                            file.id
                                        }
                                    >
                                        {
                                            file.filename ||
                                            file.original_filename
                                        }
                                    </option>
                                )
                            )}
                    </select>
                </label>
            </div>


            {/* CATEGORY */}

            {processingCategory && (
                <p>
                    Category:{" "}
                    <strong>
                        {
                            processingCategory
                        }
                    </strong>
                </p>
            )}


            {/* OPERATION */}

            {processingCategory && (
                <div>
                    <label>
                        Operation:{" "}

                        <select
                            value={
                                processingOperation
                            }
                            onChange={
                                handleProcessingOperationChange
                            }
                        >
                            {availableProcessingOperations.map(
                                (
                                    item
                                ) => (
                                    <option
                                        key={
                                            item.value
                                        }
                                        value={
                                            item.value
                                        }
                                    >
                                        {
                                            item.label
                                        }
                                    </option>
                                )
                            )}
                        </select>
                    </label>
                </div>
            )}


            {/* ========================================================
                COMPRESS OPTIONS
            ======================================================== */}

            {processingOperation ===
                "compress" && (
                <div
                    style={{
                        marginTop:
                            "15px",
                    }}
                >
                    <h4>
                        Compression
                    </h4>

                    <label>
                        Quality:{" "}

                        <input
                            type="number"
                            min="1"
                            max="100"
                            value={
                                processingOptions.quality ??
                                70
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "quality",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>

                    <p>
                        1 = smaller file,
                        100 = higher quality.
                    </p>
                </div>
            )}


            {/* ========================================================
                CONVERT OPTIONS
            ======================================================== */}

            {processingOperation ===
                "convert" && (
                <div
                    style={{
                        marginTop:
                            "15px",
                    }}
                >
                    <h4>
                        Conversion Format
                    </h4>

                    <label>
                        Format:{" "}

                        <select
                            value={
                                processingOptions.format ||
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "format",
                                    e.target
                                        .value
                                )
                            }
                        >
                            <option value="">
                                Select format
                            </option>

                            {processingCategory ===
                                "image" && (
                                <>
                                    <option value="jpg">
                                        JPG
                                    </option>

                                    <option value="png">
                                        PNG
                                    </option>

                                    <option value="webp">
                                        WEBP
                                    </option>
                                </>
                            )}

                            {processingCategory ===
                                "audio" && (
                                <>
                                    <option value="mp3">
                                        MP3
                                    </option>

                                    <option value="wav">
                                        WAV
                                    </option>

                                    <option value="ogg">
                                        OGG
                                    </option>
                                </>
                            )}

                            {processingCategory ===
                                "video" && (
                                <>
                                    <option value="mp4">
                                        MP4
                                    </option>

                                    <option value="webm">
                                        WEBM
                                    </option>

                                    <option value="avi">
                                        AVI
                                    </option>
                                </>
                            )}

                            {processingCategory ===
                                "document" && (
                                <>
                                    <option value="pdf">
                                        PDF
                                    </option>

                                    <option value="txt">
                                        TXT
                                    </option>

                                    <option value="docx">
                                        DOCX
                                    </option>
                                </>
                            )}

                            {processingCategory ===
                                "pdf" && (
                                <>
                                    <option value="pdf">
                                        PDF
                                    </option>
                                </>
                            )}
                        </select>
                    </label>
                </div>
            )}


            {/* ========================================================
                RESIZE OPTIONS
            ======================================================== */}

            {processingOperation ===
                "resize" && (
                <div
                    style={{
                        marginTop:
                            "15px",
                    }}
                >
                    <h4>
                        Resize
                    </h4>

                    <label>
                        Width:{" "}

                        <input
                            type="number"
                            min="1"
                            value={
                                processingOptions.width ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "width",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>

                    <br />

                    <label>
                        Height:{" "}

                        <input
                            type="number"
                            min="1"
                            value={
                                processingOptions.height ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "height",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>
                </div>
            )}


            {/* ========================================================
                CROP OPTIONS
            ======================================================== */}

            {processingOperation ===
                "crop" && (
                <div
                    style={{
                        marginTop:
                            "15px",
                    }}
                >
                    <h4>
                        Crop
                    </h4>

                    <label>
                        Left:{" "}

                        <input
                            type="number"
                            min="0"
                            value={
                                processingOptions.left ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "left",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>

                    <br />

                    <label>
                        Top:{" "}

                        <input
                            type="number"
                            min="0"
                            value={
                                processingOptions.top ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "top",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>

                    <br />

                    <label>
                        Right:{" "}

                        <input
                            type="number"
                            min="0"
                            value={
                                processingOptions.right ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "right",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>

                    <br />

                    <label>
                        Bottom:{" "}

                        <input
                            type="number"
                            min="0"
                            value={
                                processingOptions.bottom ??
                                ""
                            }
                            onChange={(
                                e
                            ) =>
                                updateProcessingOption(
                                    "bottom",
                                    Number(
                                        e.target
                                            .value
                                    )
                                )
                            }
                        />
                    </label>
                </div>
            )}


            {/* ========================================================
                PROCESS BUTTONS
            ======================================================== */}

            {processingFileId && (
                <div
                    style={{
                        marginTop:
                            "20px",
                    }}
                >
                    <button
                        type="button"
                        onClick={
                            handleProcess
                        }
                        disabled={
                            processing ||
                            !processingOperation
                        }
                    >
                        {processing
                            ? "Processing..."
                            : "Process File"}
                    </button>

                    <button
                        type="button"
                        onClick={
                            resetProcessing
                        }
                        disabled={
                            processing
                        }
                        style={{
                            marginLeft:
                                "10px",
                        }}
                    >
                        Reset
                    </button>
                </div>
            )}


            {/* ========================================================
                PROCESSING RESULT
            ======================================================== */}

            {processedResult && (
                <div
                    style={{
                        marginTop:
                            "20px",
                    }}
                >
                    <hr />

                    <h4>
                        Processing Complete
                    </h4>

                    <pre>
                        {JSON.stringify(
                            processedResult,
                            null,
                            2
                        )}
                    </pre>
                </div>
            )}


            <hr />


            {/* ========================================================
                WORKSPACE
            ======================================================== */}

            <h3>
                Workspace
            </h3>

            <button type="button">
                My Files
            </button>

            <button type="button">
                Processing
            </button>

            <button type="button">
                AI Tools
            </button>


            <hr />


            {/* LOGOUT */}

            <button
                type="button"
                onClick={
                    onLogout
                }
            >
                Logout
            </button>
        </div>
    );
}


export default Dashboard;