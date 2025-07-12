import customtkinter as ctk
import sys
from checker_app import CheckerApp

# Redirect output to a log file to capture all test output
sys.stdout = open("test_run_log.txt", "w", encoding="utf-8")
sys.stderr = sys.stdout

class TestRunner:
    def __init__(self, app):
        self.app = app
        self.pruefung_workflow = None
        self.controller = None
        self.view = None

    def run_tests(self):
        print("--- Starting Automated Test --- ")
        self.app.root.after(1000, self.select_pruefung_workflow)

    def select_pruefung_workflow(self):
        print("1. Selecting 'Prüfung' workflow.")
        # Directly call the main app's workflow starter
        self.app.start_workflow("pruefung_workflow")
        self.app.root.after(1000, self.get_workflow_components)

    def get_workflow_components(self):
        print("2. Accessing workflow components (controller & view).")
        # Access the currently active workflow from the app
        self.pruefung_workflow = self.app.current_workflow
        
        if self.pruefung_workflow and hasattr(self.pruefung_workflow, 'controller') and hasattr(self.pruefung_workflow, 'view'):
            self.controller = self.pruefung_workflow.controller
            self.view = self.pruefung_workflow.view
            print("   - Controller and View found.")
            self.app.root.after(1000, self.add_file_pair)
        else:
            print("   - ERROR: Could not find current_workflow or its controller/view.")
            print(f"   - Current workflow: {self.app.current_workflow}")

    def add_file_pair(self):
        print("3. Adding a file pair.")
        # We can't use filedialog, so we'll manually add a pair.
        # Create dummy files for testing
        source_path = "test_source.txt"
        target_path = "test_target.txt"
        with open(source_path, "w", encoding="utf-8") as f:
            f.write("This is the source text. It has no errrors.")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write("This is the target text. It has some errrors and misteaks.")

        pair_id = self.controller.next_file_pair_id
        self.controller.file_pairs[pair_id] = {
            'id': pair_id,
            'source_path': source_path,
            'target_path': target_path,
            'source_name': "test_source.txt",
            'target_name': "test_target.txt",
            'checks_running': False,
            'results': {}
        }
        self.controller.next_file_pair_id += 1
        self.view.update_file_pair_display(list(self.controller.file_pairs.values()))
        print(f"   - Added file pair: {self.controller.file_pairs[pair_id]['source_name']} & {self.controller.file_pairs[pair_id]['target_name']}")
        self.app.root.after(1000, self.run_checks)

    def run_checks(self):
        print("4. Starting the checks.")
        self.controller.start_checking_process()
        self.app.root.after(8000, self.verify_results) # Wait longer for checks to complete

    def verify_results(self):
        print("5. Verifying results.")
        if not self.controller.file_pairs:
            print("   - ERROR: No file pairs found after running checks.")
            self.app.root.destroy()
            return

        pair = list(self.controller.file_pairs.values())[0]
        results = pair.get("results", {})

        if not results:
            print("   - ERROR: No results were generated.")
            self.app.root.destroy()
            return

        print("   - Results received:")
        for check_id, result in results.items():
            print(f"     - {check_id}:")
            # Print first 150 chars of result
            print(f"       '{str(result)[:150]}...'")

        # Check if LanguageTool found errors
        lt_result = results.get("language_tool_check", "")
        if "Gefundene Fehler" in lt_result:
            print("   - SUCCESS: LanguageTool check seems to have worked.")
        else:
            print("   - FAILURE: LanguageTool check did not find expected errors.")
        
        # Check if KI checks ran
        ki_result = results.get("ki_qualitaetspruefung", "")
        if ki_result and "Platzhalter" not in ki_result and "Fehler" not in ki_result:
             print("   - SUCCESS: KI check seems to have worked.")
        else:
            print("   - NOTE: KI check returned a placeholder or error. This is expected if modules are not available or failed.")

        print("--- Test Finished --- ")
        self.app.root.after(2000, self.app.root.destroy)


if __name__ == "__main__":
    app = CheckerApp()
    tester = TestRunner(app)
    # Use app.root.after, as 'after' is a method of the tkinter root window
    app.root.after(1000, tester.run_tests) 
    # Use app.root.mainloop() to start the application's event loop
    app.root.mainloop()
