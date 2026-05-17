# Final Async and Deprecation Cleanup

Address the remaining `TypeError` in `page.run_task` and suppress the `DeprecationWarning` for `page.shared_preferences`.

## Proposed Changes

### main.py

- Correct `page.run_task` usage: `page.run_task(coro_func, *args)`.
- Use a simpler `warnings.simplefilter` to ensure the `DeprecationWarning` is hidden.

#### [main.py](file:///C:/Users/chris/OneDrive/Dokumente/Insane-Soundbar/Insane Control Center/Android/src/main.py)

```diff
-warnings.filterwarnings("ignore", category=DeprecationWarning, module="flet")
+warnings.simplefilter("ignore", DeprecationWarning)

...

-page.run_task(lambda: log(clean_log))
+page.run_task(log, clean_log)
```

## Verification Plan

### Automated Tests
- Run `analyze_file` again to confirm the reduction in warnings.

### Manual Verification
- Visual inspection of the code to ensure logic remains unchanged.
