#!/usr/bin/env python
"""
Wrapper script to run mobile_app.py with comm module patched
"""
import sys

# Patch comm.create_comm to return None instead of raising NotImplementedError
try:
    import comm
    original_create_comm = comm.create_comm
    
    def patched_create_comm(*args, **kwargs):
        return None
    
    comm.create_comm = patched_create_comm
except ImportError:
    pass

# Now import and run the mobile dashboard
import mobile_app

# Run the app
if __name__ == "__main__":
    mobile_app.app.run(debug=True)
