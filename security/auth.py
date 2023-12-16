# Authentication route to generate JWT token
import databases
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm


