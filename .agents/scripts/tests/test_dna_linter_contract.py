import unittest
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.dna import extract_local_imports, lint_file_dependencies, lint_dependencies_path


class DNALinterContractTests(unittest.TestCase):
    def test_extract_local_imports(self):
        dart_sample = """
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:myapp/services/api_service.dart';
import '../models/user_dto.dart';
export 'package:myapp/models/export_model.dart';
"""
        imports = extract_local_imports("dummy.dart", content=dart_sample)
        targets = [target for _, target in imports]
        self.assertIn("dart:async", targets)
        self.assertIn("package:myapp/services/api_service.dart", targets)
        self.assertIn("../models/user_dto.dart", targets)

        ts_sample = """
import React from 'react';
import { UserDto } from '../contracts/user_dto';
const authService = require('../services/auth');
"""
        ts_imports = extract_local_imports("dummy.tsx", content=ts_sample)
        ts_targets = [target for _, target in ts_imports]
        self.assertIn("react", ts_targets)
        self.assertIn("../contracts/user_dto", ts_targets)
        self.assertIn("../services/auth", ts_targets)

    def test_lint_file_dependencies_forbidden_presentation_to_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            screen_file = os.path.join(tmp, "lib", "presentation", "screens", "profile_screen.dart")
            os.makedirs(os.path.dirname(screen_file), exist_ok=True)
            content = """
import 'package:flutter/material.dart';
import 'package:myapp/services/profile_service.dart';

class ProfileScreen extends StatelessWidget {
  Widget build(BuildContext context) => Container();
}
"""
            with open(screen_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(screen_file, root_dir=tmp)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["from_tier"], "5_presentation")
            self.assertEqual(violations[0]["to_tier"], "3_services")
            self.assertIn("never bypass State controllers", violations[0]["reason"])

    def test_lint_file_dependencies_forbidden_contract_to_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract_file = os.path.join(tmp, "lib", "contracts", "user_dto.dart")
            os.makedirs(os.path.dirname(contract_file), exist_ok=True)
            content = """
import '../domain/user_validator.dart';

class UserDto {
  final String id;
  UserDto(this.id);
}
"""
            with open(contract_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(contract_file, root_dir=tmp)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["from_tier"], "1_contracts")
            self.assertEqual(violations[0]["to_tier"], "2_domain")
            self.assertIn("pure leaf definitions", violations[0]["reason"])

    def test_lint_file_dependencies_allowed_presentation_to_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            screen_file = os.path.join(tmp, "lib", "presentation", "screens", "home_screen.dart")
            os.makedirs(os.path.dirname(screen_file), exist_ok=True)
            content = """
import 'package:flutter/material.dart';
import 'package:myapp/state/home_provider.dart';

class HomeScreen extends StatelessWidget {
  Widget build(BuildContext context) => Container();
}
"""
            with open(screen_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(screen_file, root_dir=tmp)
            self.assertEqual(len(violations), 0)

    def test_chimera_detection_in_presentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            screen_file = os.path.join(tmp, "lib", "presentation", "screens", "chimera_screen.dart")
            os.makedirs(os.path.dirname(screen_file), exist_ok=True)
            content = """
import 'package:flutter/material.dart';

class ChimeraScreen extends StatelessWidget {
  void fetchData() {
    dio.get('https://api.example.com/data');
  }
}
"""
            with open(screen_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(screen_file, root_dir=tmp)
            self.assertTrue(any(v.get("imported_path") == "[CHIMERA: RAW DRIVER IN UI]" for v in violations))

    def test_feature_first_controller_classified_as_state_and_allowed_to_import_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            controller_file = os.path.join(tmp, "lib", "features", "blacklist", "presentation", "controllers", "blacklist_controller.dart")
            os.makedirs(os.path.dirname(controller_file), exist_ok=True)
            content = """
import 'package:flutter/material.dart';
import '../../data/blacklist_repository.dart';

class BlacklistController extends ChangeNotifier {
  final BlacklistRepository repo;
  BlacklistController(this.repo);
}
"""
            with open(controller_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(controller_file, root_dir=tmp)
            self.assertEqual(len(violations), 0)

    def test_feature_first_direct_screen_to_service_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            screen_file = os.path.join(tmp, "lib", "features", "blacklist", "presentation", "screens", "app_blacklist_screen.dart")
            os.makedirs(os.path.dirname(screen_file), exist_ok=True)
            content = """
import 'package:flutter/material.dart';
import '../../data/blacklist_repository.dart';

class AppBlacklistScreen extends StatelessWidget {
  Widget build(BuildContext context) => Container();
}
"""
            with open(screen_file, "w", encoding="utf-8") as f:
                f.write(content)

            violations = lint_file_dependencies(screen_file, root_dir=tmp)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["from_tier"], "5_presentation")
            self.assertEqual(violations[0]["to_tier"], "3_services")

    def test_wildcard_glob_epigenetic_aliases(self):
        from core.dna import classify_file_to_tier
        aliases = {
            "lib/features/*/data": "3_services",
            "lib/features/*/presentation/controllers": "4_state",
            "lib/features/*/domain/models": "1_contracts"
        }
        tier, _, _, _ = classify_file_to_tier("lib/features/auth/data/auth_api.dart", epigenetic_aliases=aliases)
        self.assertEqual(tier, "3_services")

        tier2, _, _, _ = classify_file_to_tier("lib/features/auth/presentation/controllers/auth_controller.dart", epigenetic_aliases=aliases)
        self.assertEqual(tier2, "4_state")

        tier3, _, _, _ = classify_file_to_tier("lib/features/auth/domain/models/user_token.dart", epigenetic_aliases=aliases)
        self.assertEqual(tier3, "1_contracts")


if __name__ == "__main__":
    unittest.main()
