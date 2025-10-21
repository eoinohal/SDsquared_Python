import { useState } from "react";

interface RunExplorerProps {
  selectedItems: string[];
  onSelectionChange: (items: string[]) => void;
}

function RunExplorer({ selectedItems, onSelectionChange }: RunExplorerProps) {
  const fileTree = {
    folders: [
      { name: "Run1", files: ["test_run_1.txt", "test_run_2.txt"] },
      { name: "Run2", files: ["test_run_3.txt", "test_run_4.txt"] },
    ],
  };

  const [expandedFolders, setExpandedFolders] = useState(
    Array(fileTree.folders.length).fill(false)
  );

  const toggleFolder = (index: number) => {
    const folder = fileTree.folders[index];
    const folderName = folder.name;

    // Prevent closing if any of its child files are selected
    const anyChildSelected = folder.files.some((file) =>
      selectedItems.includes(`${folderName}/${file}`)
    );

    if (expandedFolders[index] && anyChildSelected) return;

    const newExpanded = [...expandedFolders];
    newExpanded[index] = !newExpanded[index];
    setExpandedFolders(newExpanded);
  };

  const toggleFile = (folderName: string, fileName: string) => {
    const fullPath = `${folderName}/${fileName}`;
    const isSelected = selectedItems.includes(fullPath);

    const newSelected = isSelected
      ? selectedItems.filter((item) => item !== fullPath)
      : [...selectedItems, fullPath];

    onSelectionChange(newSelected);
  };

  // Auto-expand folders with selected files
  const computedExpandedFolders = fileTree.folders.map((folder, i) => {
    const hasSelectedChild = folder.files.some((file) =>
      selectedItems.includes(`${folder.name}/${file}`)
    );
    return hasSelectedChild ? true : expandedFolders[i];
  });

  return (
    <div className="mt-3">
      <h4>Run Explorer</h4>
      <ul className="list-group">
        {fileTree.folders.map((folder, folderIndex) => (
          <li key={folder.name} className="list-group-item p-0 border-0">
            <button
              type="button"
              className="list-group-item list-group-item-action"
              onClick={() => toggleFolder(folderIndex)}
            >
              {folder.name}
            </button>

            {computedExpandedFolders[folderIndex] && (
              <ul className="list-group list-group-flush ms-3">
                {folder.files.map((file) => {
                  const fullPath = `${folder.name}/${file}`;
                  return (
                    <li key={file} className="list-group-item p-0 border-0">
                      <button
                        type="button"
                        className={`list-group-item list-group-item-action ${
                          selectedItems.includes(fullPath) ? "active" : ""
                        }`}
                        onClick={() => toggleFile(folder.name, file)}
                      >
                        {file}
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RunExplorer;
