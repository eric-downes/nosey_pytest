# Technical Design Document: Enhancing nosey-pytest with Incremental Migration Capabilities

## 1. Executive Summary

This document outlines a comprehensive plan for enhancing our nosey-pytest toolkit with advanced capabilities for supporting incremental migrations from Python 2 with nose tests to Python 3 with pytest. The enhancement builds upon our existing codebase by adding new components for tracking migration progress, detecting compatibility issues, and implementing fallback mechanisms. Our design focuses on extending the toolkit to provide a robust migration framework that leverages Git for version control and pytest's advanced features, while maintaining functional code throughout the migration process.

## 2. Background and Motivation

Our nosey-pytest toolkit already provides capabilities for converting nose tests to pytest, but currently lacks comprehensive support for the full Python 2-to-3 migration workflow. Many legacy Python codebases still rely on Python 2 and the nose testing framework, both of which have reached end-of-life. Enhancing our toolkit to support the complete migration process offers numerous benefits:

- **Comprehensive solution**: A single toolkit for both test framework and language migration
- **Structured workflow**: Guided, step-by-step migration process with progress tracking
- **Risk reduction**: Integrated fallback mechanisms when changes cause regressions
- **Documentation automation**: Systematic recording of migration decisions and issues

However, implementing these enhancements presents several technical challenges:
- Integrating with Git for version control and rollback capabilities
- Creating a persistent tracking system for migration progress
- Implementing intelligent Python 2-to-3 pattern detection and conversion
- Preserving test functionality throughout the migration process
- Managing the interdependencies between test framework and language migration

Our enhancement plan addresses these challenges by extending our existing codebase with new modules for Git integration, migration tracking, and incremental Python 2-to-3 conversion.

## 3. Design Principles

The migration framework is built on the following core principles:

### 3.1. Test-First Migration

Converting the testing framework before tackling language compatibility ensures:
- Early detection of issues through a modern testing infrastructure
- Clear visibility of Python 2 compatibility issues
- Continuous validation throughout the Python 2-to-3 migration

### 3.2. Incremental Progress with Git Integration

- Each migration step is committed separately
- Git branching strategy isolates migration efforts from main development
- Atomic commits enable precise rollback when issues are detected
- Detailed commit messages document migration decisions

### 3.3. Fallback Mechanisms

- Automatic detection of regressions through test runs
- Immediate rollback of problematic changes using Git
- Tracking database for documenting failed migrations and strategies

### 3.4 python3 Elegance Best Left to Tailors

- Fix just enough to get the code working, and no more.  In Particular:
- Do not fix commented lines of code
- Do not fix fstrings just for readability

### 3.5. Documentation-Driven Process

- Comprehensive tracking of compatibility issues
- Migration status reporting for stakeholders
- Institutional knowledge preservation through detailed comments and commit messages

## 4. Technical Architecture

### 4.1. System Components

The enhanced migration system consists of the following components:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│ Git Integration   │◄────┤ Migration Engine  │────►│ Tracking Database │
└───────────────────┘     └───────────────────┘     └───────────────────┘
                                   ▲
         ┌─────────────────┬──────┴──────┬─────────────────┐
         ▼                 ▼             ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Nose-to-Pytest │  │ Python 2-to-3 │  │ Test Runner   │  │ Reporting     │
│ Transformer    │  │ Converter     │  │ & Validator   │  │ System        │
└───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘
```

### 4.1.1. Technical Stack and Dependencies

For implementing these components, we will leverage the following Python modules:

1. **Core Dependencies** (already in use):
   - `pytest` (>=7.0.0): For running tests and providing test markers
   - `ast` / `astor`: For AST-based transformations of nose assertions
   - `re`: For pattern matching and replacement in code

2. **New Module Dependencies**:
   - `GitPython` (>=3.1.30): For Git repository interactions
   - `lib2to3` (standard library): Foundation for Python 2-to-3 transformations
   - `modernize` (>=0.7.0, optional): For more conservative Python 2-to-3 conversions
   - `six` (>=1.16.0): For Python 2/3 compatibility in transformed code
   - `click` (>=8.1.0): For enhanced command-line interface

3. **API Integrations**:
   
   | Component            | Primary API                                   | Alternative Options                       |
   |----------------------|----------------------------------------------|------------------------------------------|
   | Git Operations       | `git.Repo` from GitPython                     | `subprocess` with git commands            |
   | AST Transformations  | `lib2to3.refactor.RefactoringTool`            | Custom AST visitors with Python's `ast`   |
   | Python 2-to-3        | `lib2to3.main`                                | `modernize.main` if available             |
   | Configuration Storage| `json` for tracking database                  | `sqlite3` for larger projects             |
   | Command-line UI      | `click` for structured commands               | `argparse` (standard library)             |

4. **Storage and State Management**:
   - JSON files (.pytest_migration.json) for tracking migration state
   - Git branches and tags for version control
   - Backup files (.bak) for immediate rollbacks

5. **Directory Structure**:
   ```
   src/
   ├── __init__.py
   ├── automigrate.py     # Existing nose-to-pytest conversion
   ├── tracking.py        # Existing tracking module
   ├── git_integration.py # New Git integration module
   ├── py2to3_migrate.py  # New Python 2-to-3 migration module
   ├── validator.py       # New test validation module
   └── report.py          # New reporting module
   ```

### 4.2. Migration Engine

The central coordination component that:
1. Orchestrates the migration process
2. Maintains state between migration phases
3. Communicates with Git for version control operations
4. Updates the tracking database

### 4.3. Nose-to-Pytest Transformer

Specialized component for converting nose test syntax to pytest:
- Converts test discovery mechanisms
- Transforms assertion methods
- Updates test decorators and fixtures
- Preserves Python 2 compatibility during conversion

### 4.4. Python 2-to-3 Converter

Tool for incrementally migrating Python 2 code to Python 3:
- Uses lib2to3 and/or modernize for syntax transformations
- Supports targeted transformations for specific modules
- Maintains configurable compatibility options (six, future)

#### 4.4.1. Python 2-to-3 Transformation Strategy

Our approach to Python 2-to-3 transformation will leverage multiple libraries with a layered strategy:

1. **Foundation Layer**: `lib2to3` from the standard library 
   - Handles basic syntax transformations (print statements, except clauses)
   - Creates AST-based transformations for accuracy
   - Provides a framework for custom fixers

2. **Enhancement Layer**: Optional integration with `modernize`
   - More conservative transformations that preserve compatibility
   - Adds `six` imports for compatibility code
   - Better handling of edge cases than basic lib2to3

3. **Custom Layer**: Project-specific transformations
   - Custom fixers for project-specific patterns
   - Special handling for known libraries and frameworks
   - Domain-specific transformations (scientific computing, web frameworks)

4. **Priority-Based Application**:
   - Critical syntax fixes first (syntax errors in Python 3)
   - Library/import compatibility second
   - Idiomatic Python 3 transformations last

5. **Configuration Options**:
   - Conservative mode: Minimal changes to make code run
   - Aggressive mode: More idiomatic Python 3 code
   - Compatibility mode: Use six for Python 2/3 compatibility
   - Pure mode: Python 3 only without compatibility layers

### 4.5. Test Runner & Validator

Executes tests after migration steps to verify functionality:
- Runs pytest with appropriate configuration
- Analyzes test results to detect regressions
- Supports marking tests as expected failures during migration

### 4.6. Tracking Database

JSON-based storage for migration metadata:
- Tracks migration status of individual files
- Records Python 2 specific patterns requiring attention
- Documents xfailed tests and their resolution status
- Maintains a history of migration attempts and outcomes

### 4.7. Reporting System

Generates comprehensive reports on migration status:
- Migration progress metrics
- Identified compatibility issues
- Successful and failed transformations
- Recommended next steps

## 5. Migration Process Workflow

The migration follows a structured, multi-phase process:

### 5.1. Phase 1: Repository Setup and Analysis

1. **Clone repository and create migration branch**
   ```bash
   git clone [repository_url]
   cd [repository_name]
   git checkout -b pytest-migration
   ```

2. **Scan codebase for nose tests and Python 2 patterns**
   - Identify test files using nose
   - Detect Python 2 specific patterns
   - Generate initial analysis report

3. **Set up tracking database**
   - Create initial tracking JSON file
   - Record baseline test status

### 5.2. Phase 2: Test Framework Migration (nose to pytest)

1. **Convert test discovery mechanisms**
   - Transform test directory structure if needed
   - Update test loading patterns

2. **Transform assertion methods**
   - Convert nose assertions to pytest equivalents
   - Replace assertX methods with raw assertions where possible

3. **Update fixtures and setup/teardown**
   - Convert nose setup/teardown to pytest fixtures
   - Transform class-based fixtures to function fixtures

4. **Identify Python 2 specific tests**
   - Detect Python 2 specific patterns in tests
   - Mark affected tests with `@pytest.mark.xfail`
   - Document issues in tracking database

5. **Test and commit changes**
   ```bash
   # Run tests with both nose and pytest to ensure equivalence
   nosetests
   pytest
   
   # Commit changes if successful
   git add .
   git commit -m "Convert nose tests to pytest format"
   ```

### 5.3. Phase 3: Incremental Python 2 to 3 Migration

1. **Prioritize modules based on dependency graph**
   - Start with foundational modules
   - Prioritize modules with fewer dependencies

2. **For each module:**
   a. **Create feature branch for module migration**
      ```bash
      git checkout -b py3-migration-[module_name]
      ```
   
   b. **Apply Python 2 to 3 transformations**
      - Apply syntax transformations
      - Update imports and dependencies
      - Address compatibility issues
   
   c. **Run tests and validate changes**
      ```bash
      pytest [module_tests] -v
      ```
   
   d. **Handle test failures:**
      - Fix compatibility issues where possible
      - Mark unresolvable issues with xfail and document
      - Rollback changes that cannot be fixed
        ```bash
        # If changes can't be fixed:
        git checkout -- [problem_files]
        ```
   
   e. **Commit successful changes**
      ```bash
      git add [module_files]
      git commit -m "Migrate [module_name] to Python 3"
      ```
   
   f. **Merge back to main migration branch**
      ```bash
      git checkout pytest-migration
      git merge py3-migration-[module_name]
      ```

3. **Update requirements and setup.py**
   - Remove Python 2 specific dependencies
   - Add Python 3 specific dependencies
   - Update version requirements

### 5.4. Phase 4: Clean-up and Finalization

1. **Remove remaining compatibility layers**
   - Remove six/future imports where no longer needed
   - Clean up any remaining compatibility code

2. **Fix previously xfailed tests**
   - Review and resolve remaining xfailed tests
   - Remove xfail markers as issues are resolved

3. **Update documentation**
   - Update README and other docs to reflect Python 3 requirement
   - Document any remaining compatibility considerations

4. **Final validation and merge**
   ```bash
   # Run full test suite
   pytest
   
   # Merge to main branch when ready
   git checkout main
   git merge pytest-migration
   ```

## 6. Key Components Implementation

### 6.1. Git Integration Module

```python
class GitIntegration:
    """Git integration for migration process."""
    
    def __init__(self, repo_path):
        """Initialize with repository path."""
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
    
    def create_branch(self, branch_name):
        """Create and switch to new branch."""
        if branch_name in [b.name for b in self.repo.branches]:
            self.repo.git.checkout(branch_name)
            return f"Switched to existing branch {branch_name}"
        else:
            self.repo.git.checkout('-b', branch_name)
            return f"Created and switched to new branch {branch_name}"
    
    def commit_changes(self, files, message):
        """Commit specified files with message."""
        for file_path in files:
            self.repo.git.add(file_path)
        
        self.repo.git.commit('-m', message)
        return f"Committed {len(files)} files"
    
    def rollback_file(self, file_path):
        """Rollback changes to specified file."""
        self.repo.git.checkout('--', file_path)
        return f"Rolled back changes to {file_path}"
    
    def file_diff(self, file_path):
        """Get diff for file compared to HEAD."""
        return self.repo.git.diff('HEAD', file_path)
    
    def merge_branch(self, source_branch):
        """Merge source branch into current branch."""
        try:
            self.repo.git.merge(source_branch)
            return f"Successfully merged {source_branch}"
        except git.GitCommandError as e:
            return f"Merge conflict: {str(e)}"
```

### 6.2. Tracking Database Module

```python
class MigrationTracker:
    """Tracks migration status and issues."""
    
    def __init__(self, project_root):
        """Initialize tracker for project."""
        self.project_root = project_root
        self.db_path = os.path.join(project_root, '.pytest_migration.json')
        self.load_database()
    
    def load_database(self):
        """Load tracking database from disk."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = self._create_initial_db()
            self.save_database()
    
    def _create_initial_db(self):
        """Create initial tracking database structure."""
        return {
            'project_root': self.project_root,
            'migration_started': datetime.now().isoformat(),
            'migrated_files': [],
            'failed_migrations': [],
            'py2_issues': {},
            'xfailed_tests': []
        }
    
    def save_database(self):
        """Save tracking database to disk."""
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_migrated_file(self, file_path, success=True, message=""):
        """Track migration status of a file."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        if success:
            if rel_path not in self.data['migrated_files']:
                self.data['migrated_files'].append(rel_path)
            
            # Remove from failed migrations if it was there
            self.data['failed_migrations'] = [
                (f, m) for f, m in self.data['failed_migrations'] 
                if f != rel_path
            ]
        else:
            # Add to failed migrations
            self.data['failed_migrations'] = [
                (f, m) for f, m in self.data['failed_migrations'] 
                if f != rel_path
            ]
            self.data['failed_migrations'].append((rel_path, message))
        
        self.save_database()
    
    def track_py2_issue(self, file_path, line_number, description, fix_strategy):
        """Track Python 2 specific issue."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        if rel_path not in self.data['py2_issues']:
            self.data['py2_issues'][rel_path] = []
        
        self.data['py2_issues'][rel_path].append({
            'line_number': line_number,
            'description': description,
            'fix_strategy': fix_strategy,
            'identified': datetime.now().isoformat(),
            'resolved': False
        })
        
        self.save_database()
    
    def track_xfailed_test(self, file_path, test_name, reason):
        """Track a test marked as xfail."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        self.data['xfailed_tests'].append({
            'file': rel_path,
            'test': test_name,
            'reason': reason,
            'marked': datetime.now().isoformat(),
            'resolved': False
        })
        
        self.save_database()
    
    def mark_issue_resolved(self, file_path, line_number):
        """Mark a Python 2 issue as resolved."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        if rel_path in self.data['py2_issues']:
            for issue in self.data['py2_issues'][rel_path]:
                if issue['line_number'] == line_number:
                    issue['resolved'] = True
                    issue['resolved_date'] = datetime.now().isoformat()
        
        self.save_database()
    
    def mark_xfail_resolved(self, file_path, test_name):
        """Mark an xfailed test as resolved."""
        rel_path = os.path.relpath(file_path, self.project_root)
        
        for test in self.data['xfailed_tests']:
            if test['file'] == rel_path and test['test'] == test_name:
                test['resolved'] = True
                test['resolved_date'] = datetime.now().isoformat()
        
        self.save_database()
    
    def generate_report(self):
        """Generate a comprehensive migration status report."""
        total_files = len(self.data['migrated_files']) + len(set(f for f, _ in self.data['failed_migrations']))
        progress = len(self.data['migrated_files']) / total_files * 100 if total_files > 0 else 0
        
        py2_issues_count = sum(len(issues) for issues in self.data['py2_issues'].values())
        resolved_issues = sum(
            1 for issues in self.data['py2_issues'].values() 
            for issue in issues if issue.get('resolved', False)
        )
        
        xfailed_count = len(self.data['xfailed_tests'])
        resolved_xfails = sum(1 for test in self.data['xfailed_tests'] if test.get('resolved', False))
        
        report = {
            'migration_progress': f"{progress:.1f}%",
            'migrated_files': len(self.data['migrated_files']),
            'failed_migrations': len(self.data['failed_migrations']),
            'py2_issues': {
                'total': py2_issues_count,
                'resolved': resolved_issues,
                'pending': py2_issues_count - resolved_issues
            },
            'xfailed_tests': {
                'total': xfailed_count,
                'resolved': resolved_xfails,
                'pending': xfailed_count - resolved_xfails
            }
        }
        
        return report
```

### 6.3. Test Detection and Validation Module

```python
class TestValidator:
    """Validates tests after migration steps."""
    
    def __init__(self, project_root, tracker):
        """Initialize validator with project root and tracker."""
        self.project_root = project_root
        self.tracker = tracker
    
    def run_pytest(self, test_path=None, xvs=True):
        """Run pytest on specified path or all tests."""
        cmd = ['pytest']
        
        if xvs:
            cmd.extend(['-xvs'])
        
        if test_path:
            cmd.append(test_path)
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def detect_py2_patterns(self, file_path):
        """Detect common Python 2 patterns in a file."""
        issues = []
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments
                if line.startswith('#'):
                    continue
                
                # Python 2 print statement
                if re.match(r'print\s+[^(]', line):
                    issues.append({
                        'line_number': i,
                        'description': 'Python 2 print statement',
                        'fix_strategy': 'Convert to print function'
                    })
                
                # Dictionary methods
                if 'iteritems()' in line:
                    issues.append({
                        'line_number': i,
                        'description': 'dict.iteritems() used',
                        'fix_strategy': 'Replace with items()'
                    })
                
                if 'iterkeys()' in line:
                    issues.append({
                        'line_number': i,
                        'description': 'dict.iterkeys() used',
                        'fix_strategy': 'Replace with keys()'
                    })
                
                # Exception handling
                if re.search(r'except\s+\w+[^,\s:]', line):
                    issues.append({
                        'line_number': i,
                        'description': 'Old-style exception syntax',
                        'fix_strategy': 'Use except ExceptionType as e:'
                    })
                
                # Unicode handling
                if re.search(r'\bu[\'"]', line):
                    issues.append({
                        'line_number': i,
                        'description': 'Unicode string literal',
                        'fix_strategy': 'Remove u prefix in Python 3'
                    })
                
                # xrange
                if re.search(r'\bxrange\b', line):
                    issues.append({
                        'line_number': i,
                        'description': 'xrange used',
                        'fix_strategy': 'Replace with range'
                    })
                
                # Long integer
                if re.search(r'\b\d+L\b', line):
                    issues.append({
                        'line_number': i,
                        'description': 'Long integer suffix used',
                        'fix_strategy': 'Remove L suffix'
                    })
                
                # More patterns can be added here
        
        # Record issues in tracker
        for issue in issues:
            self.tracker.track_py2_issue(
                file_path,
                issue['line_number'],
                issue['description'],
                issue['fix_strategy']
            )
        
        return issues
    
    def apply_xfail_markers(self, file_path, issues):
        """Apply xfail markers to tests with Python 2 issues."""
        if not issues:
            return True
            
        # Parse the file to find test functions
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        modified_lines = lines.copy()
        
        # Add pytest import if needed
        if 'import pytest' not in content:
            modified_lines.insert(0, 'import pytest')
        
        # Track which lines we've modified to avoid double-marking
        modified_line_numbers = set()
        
        # Process each issue
        for issue in issues:
            line_num = issue['line_number']
            
            # Find the closest test function above this line
            test_func_line = None
            test_name = None
            
            for i in range(line_num - 1, -1, -1):
                if i in modified_line_numbers:
                    continue
                    
                match = re.match(r'\s*def\s+(test_\w+)', lines[i])
                if match:
                    test_func_line = i
                    test_name = match.group(1)
                    break
            
            if test_func_line is not None:
                # Add the xfail decorator with reason
                decorator = f'@pytest.mark.xfail(reason="Python 2: {issue["description"]}")'
                modified_lines.insert(test_func_line, decorator)
                
                # Adjust line numbers for all subsequent modifications
                for j, issue2 in enumerate(issues):
                    if issue2['line_number'] > test_func_line:
                        issues[j]['line_number'] += 1
                
                modified_line_numbers.add(test_func_line)
                
                # Record the xfailed test
                self.tracker.track_xfailed_test(
                    file_path,
                    test_name,
                    f"Python 2: {issue['description']}"
                )
        
        # Write modified content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))
        
        return True
```

### 6.4. Migration Engine Module

```python
class MigrationEngine:
    """Coordinates the migration process."""
    
    def __init__(self, repo_path):
        """Initialize the migration engine."""
        self.repo_path = repo_path
        self.git = GitIntegration(repo_path)
        self.tracker = MigrationTracker(repo_path)
        self.validator = TestValidator(repo_path, self.tracker)
    
    def initialize_migration(self):
        """Set up migration branch and environment."""
        # Create migration branch
        result = self.git.create_branch('pytest-migration')
        print(result)
        
        # Initialize tracking database
        self.tracker.load_database()
        
        # Return success message
        return "Migration initialized successfully"
    
    def migrate_nose_to_pytest(self, test_files):
        """Migrate nose tests to pytest format."""
        from automigrate import migrate_file
        
        successful = []
        failed = []
        
        for file_path in test_files:
            rel_path = os.path.relpath(file_path, self.repo_path)
            print(f"Migrating {rel_path}...")
            
            # Apply nose to pytest transformations
            success, summary = migrate_file(file_path)
            
            if not success:
                print(f"  No transformations applied.")
                failed.append((rel_path, "No transformations applied"))
                self.tracker.track_migrated_file(file_path, success=False, message="No transformations applied")
                continue
            
            print("  Applied transformations:")
            print(summary)
            
            # Detect Python 2 specific patterns
            py2_issues = self.validator.detect_py2_patterns(file_path)
            if py2_issues:
                print(f"  Found {len(py2_issues)} Python 2 specific issues.")
                
                # Apply xfail markers to affected tests
                if len(py2_issues) > 0:
                    response = input("  Apply xfail markers to affected tests? (y/N): ")
                    if response.lower() == 'y':
                        self.validator.apply_xfail_markers(file_path, py2_issues)
                        print("  Applied xfail markers.")
            
            # Run pytest to validate
            print("  Running pytest to validate...")
            result = self.validator.run_pytest(file_path)
            
            if result['success']:
                print("  ✅ Tests passed with pytest!")
                successful.append(rel_path)
                self.tracker.track_migrated_file(file_path, success=True)
            else:
                print("  ❌ Tests failed with pytest.")
                print(f"  Error: {result['stderr']}")
                
                # Ask whether to keep the changes
                response = input("  Keep changes despite test failures? (y/N): ")
                if response.lower() == 'y':
                    print("  Keeping changes.")
                    successful.append(rel_path)
                    self.tracker.track_migrated_file(file_path, success=True)
                else:
                    print("  Rolling back changes.")
                    self.git.rollback_file(file_path)
                    failed.append((rel_path, "Tests failed with pytest"))
                    self.tracker.track_migrated_file(file_path, success=False, message="Tests failed with pytest")
        
        # Commit successful migrations
        if successful:
            commit_message = "Convert nose tests to pytest\n\n"
            commit_message += f"Successfully converted {len(successful)} test files:\n"
            
            for path in successful[:10]:
                commit_message += f"- {path}\n"
                
            if len(successful) > 10:
                commit_message += f"- and {len(successful) - 10} more files\n"
                
            self.git.commit_changes([os.path.join(self.repo_path, p) for p in successful], commit_message)
            print(f"Committed {len(successful)} migrated test files.")
        
        return successful, failed
    
    def migrate_py2_to_py3(self, module_path):
        """Migrate a module from Python 2 to Python 3."""
        from py2to3_migrate import convert_py2_to_py3
        
        # Create feature branch for module migration
        module_name = os.path.basename(module_path)
        branch_name = f"py3-migration-{module_name}"
        self.git.create_branch(branch_name)
        
        # Find Python files in the module
        py_files = []
        if os.path.isdir(module_path):
            for root, _, files in os.walk(module_path):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
        elif os.path.isfile(module_path) and module_path.endswith('.py'):
            py_files = [module_path]
        
        if not py_files:
            return [], [], f"No Python files found in {module_path}"
        
        # Apply Python 2 to 3 conversions
        successful, failed = convert_py2_to_py3(
            py_files,
            use_modernize=True,
            conservative=True,
            six_compat=True,
            backup=True
        )
        
        # Run tests to validate changes
        print(f"Running tests for {module_name}...")
        
        # Try to find related test files
        test_paths = []
        test_dir = os.path.join(self.repo_path, 'tests')
        if os.path.isdir(test_dir):
            for root, _, files in os.walk(test_dir):
                for file in files:
                    if file.startswith(f"test_{module_name}") and file.endswith('.py'):
                        test_paths.append(os.path.join(root, file))
        
        # Run all tests if no specific test files found
        if not test_paths:
            result = self.validator.run_pytest()
        else:
            # Run specific test files
            results = [self.validator.run_pytest(path) for path in test_paths]
            # Combine results
            result = {
                'success': all(r['success'] for r in results),
                'returncode': max(r['returncode'] for r in results),
                'stdout': '\n'.join(r['stdout'] for r in results),
                'stderr': '\n'.join(r['stderr'] for r in results)
            }
        
        # Handle test results
        if result['success']:
            print("✅ All tests passed!")
            
            # Commit changes
            commit_message = f"Migrate {module_name} to Python 3\n\n"
            commit_message += f"Successfully converted {len(successful)} Python files to Python 3 compatibility."
            
            self.git.commit_changes(successful, commit_message)
            print(f"Committed {len(successful)} migrated Python files.")
            
            # Merge back to main migration branch
            self.git.create_branch('pytest-migration')
            merge_result = self.git.merge_branch(branch_name)
            print(merge_result)
            
            # Update tracking database
            for file_path in successful:
                self.tracker.track_migrated_file(file_path, success=True)
                
                # Check if any xfailed tests can now be resolved
                # This would require parsing the file to find test names
                # and checking if they pass now
        else:
            print("❌ Tests failed!")
            print(result['stderr'])
            
            # Ask whether to keep the changes
            response = input("Keep changes despite test failures? (y/N): ")
            if response.lower() == 'y':
                print("Keeping changes.")
                
                # Commit changes with xfail markers
                commit_message = f"Migrate {module_name} to Python 3 (with failing tests)\n\n"
                commit_message += f"Converted {len(successful)} Python files to Python 3 compatibility.\n"
                commit_message += "Note: Some tests are still failing and marked as xfail."
                
                self.git.commit_changes(successful, commit_message)
                
                # Merge back to main migration branch
                self.git.create_branch('pytest-migration')
                merge_result = self.git.merge_branch(branch_name)
                print(merge_result)
                
                # Update tracking database
                for file_path in successful:
                    self.tracker.track_migrated_file(file_path, success=True)
            else:
                print("Rolling back changes.")
                
                # Switch back to main migration branch without merging
                self.git.create_branch('pytest-migration')
                
                # Update tracking database
                for file_path in successful:
                    self.tracker.track_migrated_file(file_path, success=False, message="Tests failed after Python 3 conversion")
        
        return successful, failed, result
    
    def generate_migration_report(self):
        """Generate comprehensive migration report."""
        report = self.tracker.generate_report()
        
        # Generate markdown report file
        report_path = os.path.join(self.repo_path, "pytest_migration_report.md")
        
        with open(report_path, 'w') as f:
            f.write("# Python 2/nose to Python 3/pytest Migration Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write("## Migration Summary\n\n")
            f.write(f"- Migration progress: {report['migration_progress']}\n")
            f.write(f"- Files successfully migrated: {report['migrated_files']}\n")
            f.write(f"- Files with failed migrations: {report['failed_migrations']}\n")
            f.write(f"- Python 2 issues identified: {report['py2_issues']['total']}\n")
            f.write(f"  - Resolved: {report['py2_issues']['resolved']}\n")
            f.write(f"  - Pending: {report['py2_issues']['pending']}\n")
            f.write(f"- Tests marked as xfail: {report['xfailed_tests']['total']}\n")
            f.write(f"  - Resolved: {report['xfailed_tests']['resolved']}\n")
            f.write(f"  - Pending: {report['xfailed_tests']['pending']}\n\n")
            
            # Failed migrations
            if self.tracker.data['failed_migrations']:
                f.write("## Failed Migrations\n\n")
                for file_path, reason in self.tracker.data['failed_migrations']:
                    f.write(f"- **{file_path}**: {reason}\n")
                f.write("\n")
            
            # Python 2 issues
            if self.tracker.data['py2_issues']:
                f.write("## Python 2 Compatibility Issues\n\n")
                for file_path, issues in self.tracker.data['py2_issues'].items():
                    f.write(f"### {file_path}\n\n")
                    for issue in issues:
                        status = "✅ RESOLVED" if issue.get('resolved', False) else "⚠️ PENDING"
                        f.write(f"- Line {issue['line_number']}: {issue['description']} ({status})\n")
                        f.write(f"  - Fix strategy: {issue['fix_strategy']}\n")
                    f.write("\n")
            
            # XFailed tests
            if self.tracker.data['xfailed_tests']:
                f.write("## XFailed Tests\n\n")
                for test in self.tracker.data['xfailed_tests']:
                    status = "✅ RESOLVED" if test.get('resolved', False) else "⚠️ PENDING"
                    f.write(f"- **{test['file']}**: {test['test']} ({status})\n")
                    f.write(f"  - Reason: {test['reason']}\n")
                f.write("\n")
            
            # Next steps
            f.write("## Next Steps\n\n")
            if report['xfailed_tests']['pending'] > 0:
                f.write("1. Fix remaining xfailed tests\n")
            if report['py2_issues']['pending'] > 0:
                f.write("2. Address remaining Python 2 compatibility issues\n")
            if report['failed_migrations'] > 0:
                f.write("3. Retry failed file migrations\n")
            f.write("4. Run full test suite to ensure all tests pass\n")
            f.write("5. Update project documentation\n")
            f.write("6. Merge migration branch to main\n")
        
        self.git.commit_changes([report_path], "Update migration report")
        
        return report_path
```

### 6.5. Command-Line Interface

```python
def main():
    """Command-line entry point for migration tool."""
    parser = argparse.ArgumentParser(
        description='Migrate Python 2/nose to Python 3/pytest'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize migration')
    init_parser.add_argument('repo_path', help='Path to repository')
    
    # Convert nose to pytest command
    nose2pytest_parser = subparsers.add_parser('nose2pytest', help='Convert nose tests to pytest')
    nose2pytest_parser.add_argument('repo_path', help='Path to repository')
    nose2pytest_parser.add_argument('--test-path', help='Specific test path or directory')
    nose2pytest_parser.add_argument('--no-xfail', action='store_true', help='Disable automatic xfail marking')
    
    # Convert Python 2 to 3 command
    py2to3_parser = subparsers.add_parser('py2to3', help='Convert Python 2 code to Python 3')
    py2to3_parser.add_argument('repo_path', help='Path to repository')
    py2to3_parser.add_argument('module_path', help='Path to module to convert')
    py2to3_parser.add_argument('--no-six', action='store_true', help='Disable six compatibility')
    py2to3_parser.add_argument('--aggressive', action='store_true', help='Use aggressive transformations')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate migration report')
    report_parser.add_argument('repo_path', help='Path to repository')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'init':
        engine = MigrationEngine(args.repo_path)
        result = engine.initialize_migration()
        print(result)
    
    elif args.command == 'nose2pytest':
        engine = MigrationEngine(args.repo_path)
        
        # Find test files
        if args.test_path:
            if os.path.isdir(args.test_path):
                test_files = []
                for root, _, files in os.walk(args.test_path):
                    for file in files:
                        if file.endswith('.py') and (file.startswith('test_') or file.endswith('_test.py')):
                            test_files.append(os.path.join(root, file))
            else:
                test_files = [args.test_path]
        else:
            # Find all test files in repository
            test_files = []
            for root, _, files in os.walk(args.repo_path):
                for file in files:
                    if file.endswith('.py') and (file.startswith('test_') or file.endswith('_test.py')):
                        # Check if it uses nose
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            if ('import nose' in content or 
                                'from nose' in content or 
                                'nose.tools' in content):
                                test_files.append(file_path)
        
        if not test_files:
            print("No nose test files found.")
            return 1
        
        print(f"Found {len(test_files)} nose test files.")
        successful, failed = engine.migrate_nose_to_pytest(test_files)
        
        print(f"\nMigration summary:")
        print(f"- Successfully migrated: {len(successful)}/{len(test_files)} files")
        
        if failed:
            print("\nFailed migrations:")
            for path, reason in failed:
                print(f"  - {path}: {reason}")
    
    elif args.command == 'py2to3':
        engine = MigrationEngine(args.repo_path)
        successful, failed, result = engine.migrate_py2_to_py3(args.module_path)
        
        module_name = os.path.basename(args.module_path)
        print(f"\nPython 2 to 3 migration summary for {module_name}:")
        print(f"- Successfully converted: {len(successful)} files")
        print(f"- Failed conversions: {len(failed)} files")
        
        if failed:
            print("\nFailed conversions:")
            for path, reason in failed:
                print(f"  - {path}: {reason}")
    
    elif args.command == 'report':
        engine = MigrationEngine(args.repo_path)
        report_path = engine.generate_migration_report()
        print(f"Migration report generated: {report_path}")
    
    return 0
```

## 7. Key Migration Scenarios and Fallback Strategies

### 7.1. Test Framework Migration Scenarios

| Scenario | Strategy | Fallback Mechanism |
|----------|----------|-------------------|
| Simple assertion migration | Convert assertion methods to raw assertions | Keep original assertion with pytest equivalent |
| Complex assertion with custom message | Preserve message in raw assertion format | Use `@pytest.mark.xfail` with detailed reason |
| Class-based test fixtures | Convert to pytest function fixtures | Temporarily keep class-based structure with pytest decorators |
| Test generator functions | Convert to pytest parametrized tests | Mark with xfail if conversion fails |
| Test setup with module-level fixtures | Convert to pytest conftest.py | Keep original structure with pytest compatibility layer |

### 7.2. Python 2-to-3 Migration Scenarios

| Scenario | Strategy | Fallback Mechanism |
|----------|----------|-------------------|
| Print statements | Convert to print functions | Mark containing test as xfail |
| Unicode/str differences | Add six.text_type conversions | Add custom helper functions for complex cases |
| Dictionary methods (iteritems, etc.) | Replace with items() + conditional six wrapper | Create compatibility functions |
| Exception handling syntax | Update to Python 3 style (except X as e) | Implement custom exception wrapper |
| Integer division | Add explicit float conversion when needed | Add compatibility imports |
| Imports reorganized in Python 3 | Update import statements with try/except | Create compatibility module |

### 7.3. Git Rollback Patterns

| Trigger | Action | Recovery Strategy |
|---------|--------|------------------|
| Test failures after migration | `git checkout -- [file]` | Document issue, add to next iteration |
| Syntax errors | Immediate rollback of affected file | Fix locally and retry |
| Import errors | Revert specific import changes | Add compatibility imports |
| Performance regressions | Revert to previous implementation | Profile and optimize separately |
| Complex failures | Create branch with partial changes | Cherry-pick working components |

## 8. Migration Tracking and Reporting

### 8.1. Progress Metrics

The migration tracking system maintains the following metrics:

- **Test framework migration progress**: Percentage of test files converted from nose to pytest
- **Python 2-to-3 migration progress**: Percentage of Python files migrated to Python 3 compatibility
- **Failed migrations**: Files that could not be automatically migrated
- **Xfailed tests**: Tests that are expected to fail during migration
- **Python 2 specific issues**: Patterns requiring migration attention

### 8.2. Migration Reports

Regular migration reports include:

- Overall migration status and progress
- Recently completed migrations
- Failed migrations with error details
- Identified Python 2 compatibility issues
- Tests marked as xfail and their resolution status
- Recommended next steps for the migration

### 8.3. Historical Tracking

The tracking database preserves a history of:

- File migration attempts
- Test status changes
- Resolution of compatibility issues
- Commit references for migration steps

## 9. Deployment and Integration

### 9.1. Installation

```bash
# Install with core dependencies
pip install nosey-pytest

# Install with Python 2-to-3 migration tools
pip install nosey-pytest[py2to3]
```

### 9.2. Continuous Integration Integration

The migration tools can be integrated with CI pipelines:

```yaml
# Example GitHub Actions workflow
name: Migration Tests

on:
  push:
    branches: [ pytest-migration ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[py2to3]
        pip install -r requirements.txt
    - name: Run tests with pytest
      run: |
        pytest
    - name: Generate migration report
      run: |
        python -m nosey_pytest report .
    - name: Upload migration report
      uses: actions/upload-artifact@v2
      with:
        name: migration-report
        path: pytest_migration_report.md
```

## 10. Conclusions and Future Work

### 10.1. Key Benefits

The incremental migration strategy offers several important benefits:

1. **Continuous functionality**: The codebase remains functional throughout the migration
2. **Manageable complexity**: Breaking the migration into well-defined phases reduces risk
3. **Clear progress tracking**: Stakeholders can monitor migration status
4. **Git integration**: Version control ensures safety and provides rollback mechanisms
5. **Documentation**: The migration process creates comprehensive documentation

### 10.2. Implementation Phases and Timeline

We propose implementing these enhancements in several phases:

#### Phase 1: Core Infrastructure (2-3 weeks)
- Git integration module
- Tracking database and persistence
- Basic CLI framework updates

#### Phase 2: Enhanced nose-to-pytest Migration (2-3 weeks)
- Python 2 pattern detection in tests
- Xfail marker management
- Test validation improvements

#### Phase 3: Python 2-to-3 Conversion (3-4 weeks)
- lib2to3 integration
- Modernize optional integration
- Custom fixers for common patterns

#### Phase 4: Reporting and Final Integration (2 weeks)
- Migration reporting system
- CI integration
- Documentation and examples

### 10.3. Potential Extensions

Future enhancements to the migration toolkit could include:

1. **IDE integration**: Plugins for popular IDEs to assist with migration tasks
2. **Dependency analysis**: Tools to analyze and update package dependencies
3. **Performance benchmarking**: Automated comparison of before/after performance
4. **Targeted transformations**: Custom transformation rules for specific libraries
5. **Multi-version testing**: Integrated testing with both Python 2 and 3

### 10.4. Development and Testing Strategy

To implement these enhancements successfully:

1. **Test-Driven Development**:
   - Create test fixtures with Python 2 patterns
   - Implement unit tests for each component
   - Use integration tests for the full migration workflow

2. **Development Environment**:
   - Python 3.7+ for development
   - Test with Python 2.7 compatibility where needed
   - Install development dependencies with `pip install -e ".[dev,py2to3]"`
   
3. **Continuous Integration**:
   - Run tests on both Python 2.7 and 3.7+ environments
   - Validate both nose and pytest compatibility
   - Generate test coverage reports

4. **Contribution Guidelines**:
   - Follow PEP 8 style guidelines
   - Include tests for all new features
   - Document public APIs with docstrings
   - Update changelog with all significant changes

By enhancing our nosey-pytest toolkit with these incremental migration capabilities, we will provide the Python community with a comprehensive solution for managing the challenging transition from Python 2/nose to Python 3/pytest while minimizing risk and maintaining functionality throughout the process.