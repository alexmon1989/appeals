const extractFileName = (path) => {
    const pathArray = path.split("/");
    return pathArray.pop();
};

const extractFilePath = (path) => {
    const pathArray = path.split("/");
    pathArray.splice(-1);
    return pathArray.join("/");
};
